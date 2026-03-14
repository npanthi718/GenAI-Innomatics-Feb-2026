from fastapi import FastAPI, Query, HTTPException, Response, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# --- DATA MODELS ---
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True

class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)

# --- DATABASE ---
# Task 1: Expanded product list (Total 7)
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook',       'price': 99,   'category': 'Stationery',  'in_stock': True},
    {'id': 3, 'name': 'USB Hub',         'price': 799,  'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',          'price': 49,   'category': 'Stationery',  'in_stock': True},
    {'id': 5, 'name': 'Laptop Stand',     'price': 1299, 'category': 'Electronics', 'in_stock': True},
    {'id': 6, 'name': 'Mechanical Keyboard', 'price': 2499, 'category': 'Electronics', 'in_stock': True},
    {'id': 7, 'name': 'Webcam',           'price': 1999, 'category': 'Electronics', 'in_stock': False},
]

cart = []
orders = []
order_counter = 1

# --- HELPER FUNCTIONS ---
def find_product(product_id: int):
    return next((p for p in products if p['id'] == product_id), None)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔵 HOME & PRODUCT VIEW ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/")
def home():
    return {"message": "Welcome to Innomatics E-commerce API"}

@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}

# Task 2: Category Filter
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    result = [p for p in products if p['category'].lower() == category_name.lower()]
    if not result:
        return {"error": "No products found in this category"}
    return {"category": category_name, "products": result}

# Task 3: In-Stock Filter
@app.get("/products/instock")
def get_instock():
    result = [p for p in products if p['in_stock']]
    return {"in_stock_products": result, "count": len(result)}

# Task 5: Search by Name
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    matched = [p for p in products if keyword.lower() in p['name'].lower()]
    if not matched:
        return {"message": "No products matched your search"}
    return {"matched_products": matched, "total_matches": len(matched)}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛒 ASSIGNMENT 4 - CART SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Q1 & Q4: Add to Cart (Handles New & Existing Items)
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Q3: Out of Stock Check
    if not product['in_stock']:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    # Q4: Check if already in cart to update qty
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            item['subtotal'] = item['quantity'] * item['unit_price']
            return {"message": "Cart updated", "cart_item": item}

    # Q1: Add new item
    new_item = {
        "product_id": product_id,
        "product_name": product['name'],
        "quantity": quantity,
        "unit_price": product['price'],
        "subtotal": product['price'] * quantity
    }
    cart.append(new_item)
    return {"message": "Added to cart", "cart_item": new_item}

# Q2: View Cart
@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty", "items": [], "grand_total": 0}
    
    grand_total = sum(item['subtotal'] for item in cart)
    return {"items": cart, "item_count": len(cart), "grand_total": grand_total}

# Q5: Remove from Cart
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    global cart
    product = next((item for item in cart if item['product_id'] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not in cart")
    
    cart = [item for item in cart if item['product_id'] != product_id]
    return {"message": f"{product['product_name']} removed from cart"}

# Q5 & Q6: Checkout
@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):
    global order_counter, cart
    # Bonus: Empty Cart Check
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")

    order_items = list(cart)
    total_price = sum(item['subtotal'] for item in order_items)
    
    new_order = {
        "order_id": order_counter,
        "customer_name": data.customer_name,
        "items": order_items,
        "grand_total": total_price,
        "status": "confirmed"
    }
    orders.append(new_order)
    order_counter += 1
    cart = [] # Clear cart
    return {"message": "Checkout successful", "order": new_order}

@app.get("/orders")
def get_orders():
    return {"orders": orders, "total_orders": len(orders)}