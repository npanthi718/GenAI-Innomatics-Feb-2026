from fastapi import FastAPI, Query, Response, status, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# ── SHARED DATA SOURCE ──────────────────────────────────────
# Task 1 (Day 1): Base product list expanded to 7 items.
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True },
    {'id': 2, 'name': 'Notebook',       'price':  99,  'category': 'Stationery',  'in_stock': True },
    {'id': 3, 'name': 'USB Hub',         'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',          'price':  49, 'category': 'Stationery',  'in_stock': True },
    {'id': 5, 'name': 'Laptop Stand',     'price': 1299, 'category': 'Electronics', 'in_stock': True },
    {'id': 6, 'name': 'Mechanical Keyboard', 'price': 2499, 'category': 'Electronics', 'in_stock': True },
    {'id': 7, 'name': 'Webcam',           'price': 1999, 'category': 'Electronics', 'in_stock': False},
]

# Temporary data stores for Day 2 POST tasks
feedback_db = []
orders_db = []


# --- Pydantic Models ---
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True

# --- Helper Functions ---
def find_product(product_id: int):
    return next((p for p in products if p['id'] == product_id), None)




# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔵 ASSIGNMENT 3 - Question Solution Given in LMS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Q5: Inventory Audit (Task 5)
@app.get('/products/audit')
def product_audit():
    in_stock_list  = [p for p in products if p['in_stock']]
    out_stock_list = [p for p in products if not p['in_stock']]
    stock_value    = sum(p['price'] * 10 for p in in_stock_list)
    priciest       = max(products, key=lambda p: p['price'])
    
    return {
        'total_products':    len(products),
        'in_stock_count':    len(in_stock_list),
        'out_of_stock_names': [p['name'] for p in out_stock_list],
        'total_stock_value':  stock_value,
        'most_expensive':    {'name': priciest['name'], 'price': priciest['price']}
    }

# ⭐ BONUS: Category-Wide Discount
@app.put('/products/discount')
def bulk_discount(
    category: str = Query(..., description='Category to discount'),
    discount_percent: int = Query(..., ge=1, le=99, description='% off'),
):
    updated = []
    for p in products:
        if p['category'].lower() == category.lower():
            p['price'] = int(p['price'] * (1 - discount_percent / 100))
            updated.append(p)
    if not updated:
        return {'message': f'No products found in category: {category}'}
    return {
        'message': f'{discount_percent}% discount applied to {category}',
        'updated_count': len(updated),
        'updated_products': updated,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔵 FASTAPI DAY 1 TASKS (E-COMMERCE BASICS)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Day 1 - Task 0: Welcome Message
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}

# Day 1 - Task 1: View all 7 Products
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

# Day 1 - Task 2: Category Filter via Path Parameter
@app.get('/products/category/{category_name}')
def get_products_by_category(category_name: str):
    result = [p for p in products if p['category'].lower() == category_name.lower()]
    if not result:
        return {"error": "No products found in this category"}
    return {"category": category_name, "products": result}

# Day 1 - Task 3: In-Stock Filter
@app.get('/products/instock')
def get_instock_products():
    result = [p for p in products if p['in_stock']]
    return {"in_stock_products": result, "count": len(result)}

# Day 1 - Task 4: Original Store Summary
@app.get('/store/summary')
def get_store_summary_v1():
    categories = list(set([p['category'] for p in products]))
    return {"total": len(products), "categories": categories}

# Day 1 - Task 5: Search by Keyword
@app.get('/products/search/{keyword}')
def search_products(keyword: str):
    matched = [p for p in products if keyword.lower() in p['name'].lower()]
    return {"matches": matched}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🟢 FASTAPI DAY 2 TASKS (ADVANCED LOGIC & VALIDATION)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Day 2 - Task 1: Filter Products by Minimum Price
# Objective: Combine existing max_price and category filters with min_price logic.
@app.get('/products/filter')
def filter_products(
    category:  str  = Query(None, description="Filter by category"),
    max_price: int  = Query(None, description="Upper price limit"),
    min_price: int  = Query(None, description="Lower price limit"), # New Day 2 param
    in_stock:  bool = Query(None, description="Check availability")
):
    result = products
    if category:
        result = [p for p in result if p['category'].lower() == category.lower()]
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
    if min_price:
        # Returns products priced at or above min_price
        result = [p for p in result if p['price'] >= min_price]
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
    
    return {'filtered_products': result, 'count': len(result)}


# Day 2 - Task 2: Lightweight Price Endpoint
# Objective: Return only name and price for a specific product ID.
@app.get('/products/{product_id}/price')
def get_product_price(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {"name": product['name'], "price": product['price']}
    return {"error": "Product not found"}


# Day 2 - Task 3: Customer Feedback with Pydantic Validation
# Objective: Validate ratings (1-5) and names (min 2 chars).
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

@app.post('/feedback')
def submit_feedback(data: CustomerFeedback):
    feedback_db.append(data.dict())
    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback_db)
    }


# Day 2 - Task 4: Business Dashboard Summary
# Objective: Comprehensive stats including cheapest/expensive items.
@app.get('/products/summary')
def get_product_summary():
    in_stock_count = len([p for p in products if p['in_stock']])
    exp = max(products, key=lambda x: x['price'])
    chp = min(products, key=lambda x: x['price'])
    
    return {
        "total_products": len(products),
        "in_stock_count": in_stock_count,
        "out_of_stock_count": len(products) - in_stock_count,
        "most_expensive": {"name": exp['name'], "price": exp['price']},
        "cheapest": {"name": chp['name'], "price": chp['price']},
        "categories": list(set(p['category'] for p in products))
    }


# Day 2 - Task 5: Validate & Place a Bulk Order
# Objective: Check stock for multiple items and return a mixed success/fail report.
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)

@app.post('/orders/bulk')
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0
    for item in order.items:
        # Search for product in the products list
        product = next((p for p in products if p['id'] == item.product_id), None)
        
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product['in_stock']:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product['price'] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product['name'], "qty": item.quantity, "subtotal": subtotal})
            
    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⭐ BONUS TASK: ORDER STATUS TRACKER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Objective: A 2-step flow using POST, GET, and PATCH.

@app.post('/orders')
def create_order(product_id: int, qty: int):
    # Orders start as "pending" instead of "confirmed"
    new_order = {
        "order_id": len(orders_db) + 1,
        "product_id": product_id,
        "quantity": qty,
        "status": "pending" 
    }
    orders_db.append(new_order)
    return new_order

@app.get('/orders/{order_id}')
def get_order_by_id(order_id: int):
    order = next((o for o in orders_db if o['order_id'] == order_id), None)
    if not order:
        return {"error": "Order not found"}
    return {"order": order}

@app.patch('/orders/{order_id}/confirm')
def confirm_order(order_id: int):
    for order in orders_db:
        if order['order_id'] == order_id:
            order['status'] = "confirmed"
            return {"message": "Order confirmed", "order": order}
    return {"error": "Order not found"}



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🟢 FASTAPI DAY 3 TASKS (CRUD APIs)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ── DAY 4 — Step 18: Add a new product (POST) ─────────────────────

@app.post('/products')

def add_product(new_product: NewProduct, response: Response):

    # Check for duplicate name (case-insensitive)
    existing_names = [p['name'].lower() for p in products]
    if new_product.name.lower() in existing_names:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Product with this name already exists'}

    # Auto-generate next ID
    next_id = max(p['id'] for p in products) + 1
    product = {
        'id':       next_id,
        'name':     new_product.name,
        'price':    new_product.price,
        'category': new_product.category,
        'in_stock': new_product.in_stock,
    }

    products.append(product)
    response.status_code = status.HTTP_201_CREATED
    return {'message': 'Product added', 'product': product}

# ── DAY 4 — Step 19: Update stock or price (PUT) ──────────────────

@app.put('/products/{product_id}')

def update_product(

    product_id: int,
    response:   Response,
    in_stock:   bool = Query(None, description='Update stock status'),
    price:      int  = Query(None, description='Update price'),

):

    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}

    if in_stock is not None:     # must use 'is not None' — False is a valid value
        product['in_stock'] = in_stock
    if price is not None:
        product['price'] = price

    return {'message': 'Product updated', 'product': product}

# ── DAY 4 — Step 20: Delete a product (DELETE) ────────────────────

@app.delete('/products/{product_id}')

def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
    products.remove(product)
    return {'message': f"Product '{product['name']}' deleted"}





