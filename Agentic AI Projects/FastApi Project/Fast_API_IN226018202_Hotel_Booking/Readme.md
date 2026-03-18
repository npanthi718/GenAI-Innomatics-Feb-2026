# Grand Stay Hotel Management System

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic" alt="Pydantic">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Swagger-Docs-85EA2D?style=for-the-badge&logo=swagger&logoColor=black" alt="Swagger Docs">
</p>

## Overview

Grand Stay Hotel API is the final FastAPI internship project for Project 3: Hotel Room Booking. It implements all 20 required questions from the assignment, covering the full flow from room listing and booking creation to check-in, check-out, search, sort, filtering, and pagination.

The project is designed as an in-memory hotel management backend for learning FastAPI fundamentals with clean endpoint organization, request validation, and workflow handling.

## Project Goals

- Complete all 20 requirements from the Hotel Room Booking brief.
- Demonstrate Day 1 to Day 6 FastAPI concepts in one project.
- Keep the API easy to test in Swagger UI.
- Present the code and documentation in a clean final-submission format.

## Tech Stack

| Component   | Technology         |
| :---------- | :----------------- |
| Framework   | FastAPI            |
| Validation  | Pydantic v2        |
| ASGI Server | Uvicorn            |
| Language    | Python 3.10+       |
| API Docs    | Swagger UI / ReDoc |

## Features Implemented

### Level 1: Beginner

- Welcome route with JSON response.
- Room inventory with total and available counts.
- Booking listing endpoint.
- Room summary endpoint with occupancy and pricing insights.
- Single-room lookup by room ID.

### Level 2: Easy

- Booking request validation using Pydantic.
- Helper functions for room lookup and stay-cost calculation.
- Booking creation with room availability checks.
- Meal-plan pricing and early-checkout discount handling.
- Room filtering using optional query parameters.

### Level 3: Medium

- Create new room with duplicate room-number prevention.
- Update room pricing and availability.
- Delete room with occupied-room protection.
- Check-in workflow.
- Check-out workflow and active bookings endpoint.

### Level 4: Hard

- Room search by room number or type.
- Room sorting by price, floor, or room type.
- Room pagination.
- Booking search and booking sort.
- Unified room browse endpoint combining search, sort, and pagination.

## Endpoint Map

| Method | Endpoint               | Purpose                           |
| :----- | :--------------------- | :-------------------------------- |
| GET    | /                      | Welcome route                     |
| GET    | /rooms                 | List all rooms                    |
| GET    | /rooms/summary         | Room summary and breakdown        |
| GET    | /rooms/filter          | Filter rooms                      |
| GET    | /rooms/search          | Search rooms                      |
| GET    | /rooms/sort            | Sort rooms                        |
| GET    | /rooms/page            | Paginate rooms                    |
| GET    | /rooms/browse          | Combined search, sort, pagination |
| GET    | /rooms/{room_id}       | Get one room                      |
| POST   | /rooms                 | Add room                          |
| PUT    | /rooms/{room_id}       | Update room                       |
| DELETE | /rooms/{room_id}       | Delete room                       |
| GET    | /bookings              | List all bookings                 |
| POST   | /bookings              | Create booking                    |
| GET    | /bookings/active       | List active bookings              |
| GET    | /bookings/search       | Search bookings by guest          |
| GET    | /bookings/sort         | Sort bookings                     |
| POST   | /checkin/{booking_id}  | Check in guest                    |
| POST   | /checkout/{booking_id} | Check out guest                   |

## Request Models

### BookingRequest

- `guest_name`: string, minimum 2 characters
- `room_id`: integer, greater than 0
- `nights`: integer, greater than 0 and less than or equal to 30
- `phone`: string, minimum 10 characters
- `meal_plan`: string, default `none`
- `early_checkout`: boolean, default `False`

### NewRoom

- `room_number`: string
- `type`: string
- `price_per_night`: integer
- `floor`: integer
- `is_available`: boolean, default `True`

## How to Run

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the API server

```bash
uvicorn main:app --reload
```

### 4. Open the API documentation

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Suggested Swagger Test Flow

To verify the complete workflow in a sensible order:

1. Test `GET /rooms` and `GET /rooms/summary`.
2. Create a booking with `POST /bookings`.
3. Confirm the room becomes unavailable.
4. Check in with `POST /checkin/{booking_id}`.
5. View `GET /bookings/active`.
6. Check out with `POST /checkout/{booking_id}`.
7. Test filter, search, sort, page, and browse endpoints.
8. Test CRUD operations for room creation, update, and deletion.

## Project Structure

```text
.
|-- main.py
|-- Readme.md
|-- requirements.txt
|-- .gitignore
|-- fastapi_final_project.html
|-- Output Screenshots
```

## Notes

- This project uses in-memory Python lists instead of a database.
- Data resets whenever the server restarts.
- Fixed routes are placed above variable routes to avoid FastAPI path conflicts.

## Final Submission Status

- Project selected: Project 3 - Hotel Room Booking
- All 20 questions covered in `main.py`
- README cleaned and submission-ready
- Requirements and `.gitignore` reviewed

## Developer

Sushil Panthi  
Full Stack Developer | Agentic AI Specialist  
You can learn more about me on my [personal website](https://www.sushilpanthi.com).  
🚀 Connect with me: [LinkedIn](https://www.linkedin.com/in/sushilpanthi/) | [GitHub](https://github.com/npanthi718)


<p align="center">
Built with ✨ for the <b>FastAPI Internship Final Submission</b>
