from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# Product Data Model
class Product(BaseModel):
    name: str
    price: float
    category: str
    in_stock: bool



# Initial Product Inventory (4 products already exist)

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 3, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "Pen Pack", "price": 59, "category": "Stationery", "in_stock": True}
]

# Function to auto generate product ID
def generate_id():
    return max(p["id"] for p in products) + 1



# Q1 – Product Registration API
@app.post("/products", status_code=201)
def add_product(product: Product):

    # Prevent duplicate product names
    for p in products:
        if p["name"].lower() == product.name.lower():
            raise HTTPException(status_code=400, detail="Product already exists")

    new_product = {
        "id": generate_id(),
        **product.dict()
    }

    products.append(new_product)

    return {
        "message": "Product added successfully",
        "product": new_product
    }



# Q2 – Update Product Stock Status
@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product):

    for i, p in enumerate(products):
        if p["id"] == product_id:
            products[i] = {
                "id": product_id,
                **product.dict()
            }
            return {
                "message": "Product updated successfully",
                "product": products[i]
            }

    raise HTTPException(status_code=404, detail="Product not found")



# Q3 – Remove Discontinued Product
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for i, p in enumerate(products):
        if p["id"] == product_id:
            deleted = products.pop(i)
            return {
                "message": "Product deleted successfully",
                "product": deleted
            }

    raise HTTPException(status_code=404, detail="Product not found")



# Q4 – Inventory Test Workflow
@app.get("/products")
def get_all_products():

    return {
        "total_products": len(products),
        "products": products
    }



# Q5 – Inventory Audit Report
@app.get("/products/audit")
def inventory_audit():

    total = len(products)
    in_stock = sum(1 for p in products if p["in_stock"])
    out_stock = total - in_stock

    return {
        "total_products": total,
        "in_stock_products": in_stock,
        "out_of_stock_products": out_stock
    }


# BONUS – Category Discount API

@app.put("/products/discount/{category}")
def apply_discount(category: str, discount: float):

    updated_products = []

    for p in products:
        if p["category"].lower() == category.lower():
            p["price"] = round(p["price"] * (1 - discount / 100), 2)
            updated_products.append(p)

    if not updated_products:
        raise HTTPException(status_code=404, detail="Category not found")

    return {
        "message": f"{discount}% discount applied to {category} category",
        "products": updated_products
    }