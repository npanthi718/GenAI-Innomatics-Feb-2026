from fastapi import FastAPI, Query

app = FastAPI()

# ── DATA SOURCE: Temporary Product Database ──────────────────
# TASK 1: Expanded the product list to include IDs 5, 6, and 7.
# Each product now includes: id, name, price, category, and in_stock status.
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True },
    {'id': 2, 'name': 'Notebook',       'price':  99,  'category': 'Stationery',  'in_stock': True },
    {'id': 3, 'name': 'USB Hub',         'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',          'price':  49, 'category': 'Stationery',  'in_stock': True },
    {'id': 5, 'name': 'Laptop Stand',     'price': 1299, 'category': 'Electronics', 'in_stock': True },
    {'id': 6, 'name': 'Mechanical Keyboard', 'price': 2499, 'category': 'Electronics', 'in_stock': True },
    {'id': 7, 'name': 'Webcam',           'price': 1999, 'category': 'Electronics', 'in_stock': False},
]

# ── HOME ENDPOINT ───────────────────────────────────────────
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}

# ── TASK 1: Get All Products ────────────────────────────────
# Confirming that 'total' now shows 7 products.
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

# ── TASK 2: Category Filter Endpoint ───────────────────────
# Uses path parameter {category_name} to filter items.
# Returns a custom error message if the category is empty.
@app.get('/products/category/{category_name}')
def get_products_by_category(category_name: str):
    result = [p for p in products if p['category'].lower() == category_name.lower()]
    if not result:
        return {"error": "No products found in this category"}
    return {"category": category_name, "products": result}

# ── TASK 3: In-Stock Only Endpoint ─────────────────────────
# Returns only items where in_stock is True, along with a count.
@app.get('/products/instock')
def get_instock_products():
    result = [p for p in products if p['in_stock']]
    return {"in_stock_products": result, "count": len(result)}

# ── TASK 4: Store Summary Endpoint ─────────────────────────
# Returns total, in-stock, and out-of-stock counts plus unique categories.
@app.get('/store/summary')
def get_store_summary():
    in_stock_count = len([p for p in products if p['in_stock']])
    unique_categories = list(set([p['category'] for p in products]))
    
    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": len(products) - in_stock_count,
        "categories": unique_categories
    }

# ── TASK 5: Case-Insensitive Name Search ───────────────────
# Searches for a keyword within the product names.
@app.get('/products/search/{keyword}')
def search_products(keyword: str):
    matched = [p for p in products if keyword.lower() in p['name'].lower()]
    if not matched:
        return {"message": "No products matched your search"}
    return {"search_keyword": keyword, "matched_products": matched, "total_matches": len(matched)}

# ── BONUS TASK: Cheapest & Most Expensive Products ──────────
# Identifies 'Best Deal' (lowest price) and 'Premium Pick' (highest price).
@app.get('/products/deals')
def get_product_deals():
    # min and max used to find products based on price key
    best_deal = min(products, key=lambda x: x['price'])
    premium_pick = max(products, key=lambda x: x['price'])
    
    return {
        "best_deal": best_deal,
        "premium_pick": premium_pick
    }

# ── ORIGINAL ID FILTER ─────────────────────────────────────
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}