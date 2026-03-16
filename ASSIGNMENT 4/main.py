from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# -----------------------------
# Product Database
# -----------------------------
products = {
    1: {"name": "Wireless Mouse", "price": 499, "in_stock": True},
    2: {"name": "Notebook", "price": 99, "in_stock": True},
    3: {"name": "USB Hub", "price": 799, "in_stock": False},
    4: {"name": "Pen Set", "price": 49, "in_stock": True}
}

# Cart and Orders storage
cart = []
orders = []
order_counter = 1


# Request body model for checkout
class Checkout(BaseModel):
    customer_name: str
    delivery_address: str


# Helper function to calculate subtotal
def calculate_total(product, quantity):
    return product["price"] * quantity



# Q1: Add Items to the Cart

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    # Check if product exists
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[product_id]

    # Q3: Check if product is out of stock
    if not product["in_stock"]:
        raise HTTPException(
            status_code=400,
            detail=f"{product['name']} is out of stock"
        )

   
    # Q4: If product already exists in cart, update quantity
    
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_total(product, item["quantity"])

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    # Add new item to cart
    new_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": calculate_total(product, quantity)
    }

    cart.append(new_item)

    return {
        "message": "Added to cart",
        "cart_item": new_item
    }


# Q2: View the Cart and Verify the Total

@app.get("/cart")
def view_cart():

    # Bonus: If cart is empty
    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


# ==========================================================
# Q5: Remove an Item from Cart
# Endpoint: DELETE /cart/{product_id}
# Removes a product from the cart
# ==========================================================
@app.delete("/cart/{product_id}")
def remove_item(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}

    raise HTTPException(status_code=404, detail="Item not found in cart")



# Q5: Checkout Cart

@app.post("/cart/checkout")
def checkout(data: Checkout):

    global order_counter

    # Bonus: Handle checkout when cart is empty
    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )

    orders_placed = []
    grand_total = 0

    for item in cart:

        order = {
            "order_id": order_counter,
            "customer_name": data.customer_name,
            "delivery_address": data.delivery_address,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }

        orders.append(order)
        orders_placed.append(order)

        grand_total += item["subtotal"]
        order_counter += 1

    # Clear cart after checkout
    cart.clear()

    return {
        "message": "Order placed successfully",
        "orders_placed": orders_placed,
        "grand_total": grand_total
    }



# Q6: View Orders List
@app.get("/orders")
def view_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }