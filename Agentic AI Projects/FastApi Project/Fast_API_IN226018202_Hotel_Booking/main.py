import math
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator


app = FastAPI(
    title="Grand Stay Hotel API",
    description="A FastAPI final project that covers all 20 requirements for the Hotel Room Booking domain.",
    version="1.0.0",
)


class BookingRequest(BaseModel):
    guest_name: str = Field(..., description="Guest full name")
    room_id: int = Field(..., description="Existing room ID")
    nights: int = Field(..., description="Length of stay")
    phone: str = Field(..., description="Guest contact number")
    meal_plan: str = Field(
        default="none",
        description="Meal plan: none, breakfast, or all-inclusive",
    )
    early_checkout: bool = Field(default=False, description="Apply 10% discount when true")

    @field_validator("guest_name")
    @classmethod
    def validate_guest_name(cls, value: str) -> str:
        cleaned_name = value.strip()
        if len(cleaned_name) < 2:
            raise ValueError("Guest name should be at least 2 characters.")
        return cleaned_name

    @field_validator("room_id")
    @classmethod
    def validate_room_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Room ID should be greater than 0.")
        return value

    @field_validator("nights")
    @classmethod
    def validate_nights(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Stay should be at least 1 night.")
        if value > 30:
            raise ValueError("Cannot be booked for more than 30 days.")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        cleaned_phone = value.strip()
        if len(cleaned_phone) < 10:
            raise ValueError("Phone number should be at least 10 digits.")
        if not cleaned_phone.isdigit():
            raise ValueError("Phone number should contain only digits.")
        return cleaned_phone

    @field_validator("meal_plan")
    @classmethod
    def validate_meal_plan(cls, value: str) -> str:
        normalized_plan = value.strip().lower().replace("_", "-")
        if normalized_plan not in ALLOWED_MEAL_PLANS:
            raise ValueError("Meal plan should be one of: none, breakfast, all-inclusive or all_inclusive.")
        return normalized_plan


class NewRoom(BaseModel):
    room_number: str = Field(..., min_length=1, description="Unique room number")
    type: str = Field(..., min_length=2, description="Single, Double, Suite, or Deluxe")
    price_per_night: int = Field(..., gt=0)
    floor: int = Field(..., gt=0)
    is_available: bool = True


rooms = [
    {"id": 1, "room_number": "101", "type": "Single", "price_per_night": 1500, "floor": 1, "is_available": True},
    {"id": 2, "room_number": "102", "type": "Double", "price_per_night": 2500, "floor": 1, "is_available": True},
    {"id": 3, "room_number": "201", "type": "Suite", "price_per_night": 5000, "floor": 2, "is_available": False},
    {"id": 4, "room_number": "202", "type": "Deluxe", "price_per_night": 3500, "floor": 2, "is_available": True},
    {"id": 5, "room_number": "301", "type": "Single", "price_per_night": 1600, "floor": 3, "is_available": True},
    {"id": 6, "room_number": "302", "type": "Suite", "price_per_night": 5500, "floor": 3, "is_available": True},
    {"id": 7, "room_number": "401", "type": "Double", "price_per_night": 2700, "floor": 4, "is_available": False},
    {"id": 8, "room_number": "402", "type": "Deluxe", "price_per_night": 3800, "floor": 4, "is_available": True},
    {"id": 9, "room_number": "501", "type": "Single", "price_per_night": 1700, "floor": 5, "is_available": True},
    {"id": 10, "room_number": "502", "type": "Suite", "price_per_night": 6000, "floor": 5, "is_available": True},
]

bookings = []
booking_counter = 1

ALLOWED_MEAL_PLANS = {"none", "breakfast", "all-inclusive"}
ROOM_SORT_FIELDS = {"price_per_night", "floor", "type"}
BOOKING_SORT_FIELDS = {"total_cost", "nights"}


def clean_validation_message(message: str) -> str:
    if message.lower().startswith("value error, "):
        return message.split(", ", 1)[1]
    return message


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    for error in exc.errors():
        if error.get("type") == "json_invalid":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Invalid JSON format. Please check commas, quotes, and brackets in the request body.",
                    "details": error.get("msg", "Malformed JSON request body."),
                },
            )

    friendly_errors = []
    for error in exc.errors():
        location = error.get("loc", [])
        field_name_parts = [str(part) for part in location[1:]] if len(location) > 1 else []
        field_name = ".".join(field_name_parts) if field_name_parts else "request"
        raw_message = error.get("msg", "Invalid value.")

        if error.get("type") == "missing":
            pretty_field = field_name.replace("_", " ")
            message = f"{pretty_field.capitalize()} is required."
        else:
            message = clean_validation_message(raw_message)

        friendly_errors.append(
            {
                "field": field_name,
                "message": message,
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Some input values are invalid. Please correct them and try again.",
            "errors": friendly_errors,
        },
    )


def find_room(room_id: int) -> Optional[dict]:
    return next((room for room in rooms if room["id"] == room_id), None)


def find_booking(booking_id: int) -> Optional[dict]:
    return next((booking for booking in bookings if booking["booking_id"] == booking_id), None)


def count_rooms_by_type(room_list: list[dict]) -> dict[str, int]:
    breakdown: dict[str, int] = {}
    for room in room_list:
        room_type = room["type"]
        breakdown[room_type] = breakdown.get(room_type, 0) + 1
    return breakdown


def calculate_stay_cost(
    price_per_night: int,
    nights: int,
    meal_plan: str,
    early_checkout: bool = False,
) -> tuple[int, int]:
    normalized_meal_plan = meal_plan.strip().lower().replace("_", "-")

    if normalized_meal_plan not in ALLOWED_MEAL_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="meal_plan must be one of: none, breakfast, all-inclusive or all_inclusive",
        )

    meal_cost_per_night = 0
    if normalized_meal_plan == "breakfast":
        meal_cost_per_night = 500
    elif normalized_meal_plan == "all-inclusive":
        meal_cost_per_night = 1200

    total = (price_per_night + meal_cost_per_night) * nights
    discount = int(total * 0.10) if early_checkout else 0
    return total - discount, discount


def filter_rooms_logic(
    room_type: Optional[str] = None,
    max_price: Optional[int] = None,
    floor: Optional[int] = None,
    is_available: Optional[bool] = None,
) -> list[dict]:
    filtered_rooms = rooms
    if room_type is not None:
        filtered_rooms = [room for room in filtered_rooms if room["type"].lower() == room_type.lower()]
    if max_price is not None:
        filtered_rooms = [room for room in filtered_rooms if room["price_per_night"] <= max_price]
    if floor is not None:
        filtered_rooms = [room for room in filtered_rooms if room["floor"] == floor]
    if is_available is not None:
        filtered_rooms = [room for room in filtered_rooms if room["is_available"] == is_available]
    return filtered_rooms


def validate_sorting(sort_by: str, order: str, allowed_fields: set[str]) -> None:
    if sort_by not in allowed_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"sort_by must be one of: {', '.join(sorted(allowed_fields))}",
        )
    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="order must be either asc or desc",
        )


def paginate_items(items: list[dict], page: int, limit: int) -> dict:
    start = (page - 1) * limit
    total_items = len(items)
    total_pages = math.ceil(total_items / limit) if total_items else 0
    return {
        "page": page,
        "limit": limit,
        "total": total_items,
        "total_pages": total_pages,
        "results": items[start : start + limit],
    }


@app.get("/", tags=["Level 1: Beginner"])
def home():
    return {"message": "Welcome to Grand Stay Hotel"}


@app.get("/rooms", tags=["Level 1: Beginner"])
def get_all_rooms():
    available_count = len([room for room in rooms if room["is_available"]])
    return {"rooms": rooms, "total": len(rooms), "available_count": available_count}


@app.get("/bookings", tags=["Level 1: Beginner"])
def get_all_bookings():
    return {"bookings": bookings, "total": len(bookings)}


@app.get("/rooms/summary", tags=["Level 1: Beginner"])
def get_rooms_summary():
    available_rooms = [room for room in rooms if room["is_available"]]
    return {
        "total_rooms": len(rooms),
        "available_count": len(available_rooms),
        "occupied_count": len(rooms) - len(available_rooms),
        "cheapest_room_price": min(room["price_per_night"] for room in rooms),
        "most_expensive_room_price": max(room["price_per_night"] for room in rooms),
        "room_type_breakdown": count_rooms_by_type(rooms),
    }


@app.post("/bookings", tags=["Level 2: Easy"])
def place_booking(booking_request: BookingRequest):
    global booking_counter

    room = find_room(booking_request.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    if not room["is_available"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room is occupied")

    total_cost, discount = calculate_stay_cost(
        price_per_night=room["price_per_night"],
        nights=booking_request.nights,
        meal_plan=booking_request.meal_plan,
        early_checkout=booking_request.early_checkout,
    )

    room["is_available"] = False
    booking = {
        "booking_id": booking_counter,
        "guest_name": booking_request.guest_name,
        "phone": booking_request.phone,
        "room_id": room["id"],
        "room_details": room.copy(),
        "nights": booking_request.nights,
        "meal_plan": booking_request.meal_plan,
        "early_checkout": booking_request.early_checkout,
        "total_cost": total_cost,
        "discount_applied": discount,
        "status": "confirmed",
    }
    bookings.append(booking)
    booking_counter += 1
    return booking


@app.get("/bookings/calculate", tags=["Level 2: Easy"])
def calculate_booking_cost(
    room_id: int = Query(..., gt=0),
    nights: int = Query(..., gt=0, le=30),
    meal_plan: str = Query(default="none"),
    early_checkout: bool = Query(default=False),
):
    room = find_room(room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    total_cost, discount = calculate_stay_cost(
        price_per_night=room["price_per_night"],
        nights=nights,
        meal_plan=meal_plan,
        early_checkout=early_checkout,
    )

    return {
        "message": "Estimated booking cost calculated successfully.",
        "room_id": room_id,
        "room_number": room["room_number"],
        "price_per_night": room["price_per_night"],
        "nights": nights,
        "meal_plan": meal_plan.strip().lower().replace("_", "-"),
        "early_checkout": early_checkout,
        "discount_applied": discount,
        "estimated_total_cost": total_cost,
    }


@app.get("/rooms/filter", tags=["Level 2: Easy"])
def filter_rooms(
    type: Optional[str] = Query(default=None),
    max_price: Optional[int] = Query(default=None, gt=0),
    floor: Optional[int] = Query(default=None, gt=0),
    is_available: Optional[bool] = Query(default=None),
):
    filtered_rooms = filter_rooms_logic(type, max_price, floor, is_available)
    return {"filtered_rooms": filtered_rooms, "count": len(filtered_rooms)}


@app.post("/rooms", status_code=status.HTTP_201_CREATED, tags=["Level 3: Medium"])
def add_room(room_data: NewRoom):
    if any(room["room_number"].lower() == room_data.room_number.lower() for room in rooms):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room number already exists")

    new_room = {"message":"New Room Added Successfully", "id": max(room["id"] for room in rooms) + 1, **room_data.model_dump()}
    rooms.append(new_room)
    return new_room



@app.post("/checkin/{booking_id}", tags=["Level 3: Medium - Workflow"])
def check_in(booking_id: int):
    booking = find_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking["status"] != "confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only confirmed bookings can be checked in",
        )

    booking["status"] = "checked_in"
    return {"message": "Guest checked in successfully", "booking": booking}


@app.post("/checkout/{booking_id}", tags=["Level 3: Medium - Workflow"])
def check_out(booking_id: int):
    booking = find_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking["status"] != "checked_in":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only checked-in bookings can be checked out",
        )

    booking["status"] = "checked_out"
    room = find_room(booking["room_id"])
    if room:
        room["is_available"] = True
    return {"message": "Guest checked out and room is available again", "booking": booking}


@app.get("/bookings/active", tags=["Level 3: Medium - Workflow"])
def get_active_bookings():
    active_bookings = [booking for booking in bookings if booking["status"] in {"confirmed", "checked_in"}]
    return {"active_bookings": active_bookings, "count": len(active_bookings)}


@app.get("/rooms/search", tags=["Level 4: Hard"])
def search_rooms(keyword: str = Query(..., min_length=1)):
    normalized_keyword = keyword.lower()
    matches = [
        room
        for room in rooms
        if normalized_keyword in room["room_number"].lower() or normalized_keyword in room["type"].lower()
    ]
    if not matches:
        return {"message": f'No rooms matched the keyword "{keyword}".', "total_found": 0, "matches": []}
    return {"keyword": keyword, "total_found": len(matches), "matches": matches}


@app.get("/rooms/sort", tags=["Level 4: Hard"])
def sort_rooms(
    sort_by: str = Query(default="price_per_night"),
    order: str = Query(default="asc"),
):
    validate_sorting(sort_by, order, ROOM_SORT_FIELDS)
    sorted_rooms = sorted(rooms, key=lambda room: room[sort_by], reverse=order == "desc")
    return {"sorted_by": sort_by, "order": order, "rooms": sorted_rooms}


@app.get("/rooms/page", tags=["Level 4: Hard"])
def paginate_rooms(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=2, ge=1),
):
    pagination = paginate_items(rooms, page, limit)
    return {
        "page": pagination["page"],
        "limit": pagination["limit"],
        "total": pagination["total"],
        "total_pages": pagination["total_pages"],
        "rooms": pagination["results"],
    }


@app.get("/bookings/search", tags=["Level 4: Hard"])
def search_bookings(guest_name: str = Query(..., min_length=1)):
    normalized_guest_name = guest_name.lower()
    matches = [booking for booking in bookings if normalized_guest_name in booking["guest_name"].lower()]
    return {"guest_name": guest_name, "total_found": len(matches), "matches": matches}


@app.get("/bookings/sort", tags=["Level 4: Hard"])
def sort_bookings(
    sort_by: str = Query(default="total_cost"),
    order: str = Query(default="asc"),
):
    validate_sorting(sort_by, order, BOOKING_SORT_FIELDS)
    sorted_bookings = sorted(bookings, key=lambda booking: booking[sort_by], reverse=order == "desc")
    return {"sorted_by": sort_by, "order": order, "bookings": sorted_bookings}


@app.get("/rooms/browse", tags=["Level 4: Hard"])
def browse_rooms(
    keyword: Optional[str] = Query(default=None),
    sort_by: str = Query(default="price_per_night"),
    order: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=3, ge=1),
):
    validate_sorting(sort_by, order, ROOM_SORT_FIELDS)

    filtered_rooms = rooms
    if keyword is not None:
        normalized_keyword = keyword.lower()
        filtered_rooms = [
            room
            for room in filtered_rooms
            if normalized_keyword in room["room_number"].lower() or normalized_keyword in room["type"].lower()
        ]

    sorted_rooms = sorted(filtered_rooms, key=lambda room: room[sort_by], reverse=order == "desc")
    pagination = paginate_items(sorted_rooms, page, limit)
    return {
        "keyword": keyword,
        "sorted_by": sort_by,
        "order": order,
        "page": pagination["page"],
        "limit": pagination["limit"],
        "total": pagination["total"],
        "total_pages": pagination["total_pages"],
        "results": pagination["results"],
    }


@app.get("/rooms/{room_id}", tags=["Standard CRUD"])
def get_single_room(room_id: int):
    room = find_room(room_id)
    if not room:
        return {"error": "Room not found"}
    return {"room": room}


@app.put("/rooms/{room_id}", tags=["Standard CRUD"])
def update_room(
    room_id: int,
    price_per_night: Optional[int] = Query(default=None, gt=0),
    is_available: Optional[bool] = Query(default=None),
):
    room = find_room(room_id)

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    if price_per_night is not None:
        room["price_per_night"] = price_per_night
    if is_available is not None:
        room["is_available"] = is_available
    return room


@app.delete("/rooms/{room_id}", tags=["Standard CRUD"])
def delete_room(room_id: int):
    room = find_room(room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    if not room["is_available"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete an occupied room",
        )

    rooms.remove(room)
    return {"message": f"Room {room['room_number']} deleted successfully"}