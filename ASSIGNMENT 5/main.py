from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics"},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery"},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics"},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery"}
]

orders = []

class OrderRequest(BaseModel):
    customer_name: str
    product_id: int
    quantity: int = 1

@app.get("/products/search")
def search_products(keyword: str):
    results = [p for p in products if keyword.lower() in p['name'].lower()]
    if not results:
        return {"message": f"No products found for: {keyword}"}
    return {"total_found": len(results), "products": results}

@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ['price', 'name']:
        return {"message": "sort_by must be 'price' or 'name'"}
        
    reverse = (order == 'desc')
    result = sorted(products, key=lambda p: p[sort_by], reverse=reverse)
    return {"sort_by": sort_by, "order": order, "products": result}

@app.get("/products/page")
def page_products(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    paged = products[start : start + limit]
    return {
        "page": page,
        "limit": limit,
        "total_pages": -(-len(products) // limit),
        "products": paged
    }


@app.get('/orders/search')
def search_orders(customer_name: str = Query(...)):
    results = [o for o in orders if customer_name.lower() in o['customer_name'].lower()]
    if not results:
        return {'message': f'No orders found for: {customer_name}'}
    return {'customer_name': customer_name, 'total_found': len(results), 'orders': results}

@app.get('/products/sort-by-category')
def sort_by_category():
    result = sorted(products, key=lambda p: (p['category'], p['price']))
    return {'products': result, 'total': len(result)}

@app.get('/products/browse')
def browse_products(
    keyword: str = Query(None),
    sort_by: str = Query('price'),
    order:   str = Query('asc'),
    page:    int = Query(1, ge=1),
    limit:   int = Query(4, ge=1, le=20)
):
    result = products
    if keyword:
        result = [p for p in result if keyword.lower() in p['name'].lower()]
    
    if sort_by in ['price', 'name']:
        result = sorted(result, key=lambda p: p[sort_by], reverse=(order=='desc'))
        
    total  = len(result)
    start  = (page - 1) * limit
    paged  = result[start : start + limit]
    
    return {
        'keyword': keyword, 'sort_by': sort_by, 'order': order,
        'page': page, 'limit': limit, 'total_found': total,
        'total_pages': -(-total // limit) if limit > 0 else 0,
        'products': paged
    }

@app.get('/orders/page')
def get_orders_paged(
    page:  int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20)
):
    start = (page - 1) * limit
    return {
        'page': page,
        'limit': limit,
        'total': len(orders),
        'total_pages': -(-len(orders) // limit) if limit > 0 else 0,
        'orders': orders[start : start + limit]
    }

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/orders")
def place_order(order: OrderRequest):
    new_order = {
        "order_id": len(orders) + 1,
        "customer_name": order.customer_name,
        "product_id": order.product_id,
        "quantity": order.quantity
    }
    orders.append(new_order)
    return {"message": "Order placed successfully", "order": new_order}

@app.get("/orders")
def all_orders():
    return {"orders": orders, "total_orders": len(orders)}
