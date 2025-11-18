# =============================================
# FILE: main.py (FastAPI) - FINAL COMPLETE VERSION
# =============================================

import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import (Column, Integer, String, Float, Boolean, 
                        Date, DateTime, ForeignKey, func)
from sqlalchemy.orm import Session

# Assuming these files are correctly set up in your project
from database import SessionLocal, engine, Base
from schemas import (ProductCreate, ProductUpdate, ProductResponse,
                   OrderCreate, OrderUpdate, OrderResponse,
                   MessageResponse, DjangoOrderResponse,
                   CustomerCreate, CustomerResponse)


# =============================================
# PYDANTIC SCHEMA - REQUIRED FOR ANALYSIS ENDPOINTS
# =============================================
class ProductAnalysisResponse(BaseModel):
    product_id: int
    product_name: str
    total_revenue: Optional[float] = 0.0
    total_quantity_sold: Optional[int] = 0

    class Config:
        from_attributes = True


# =============================================
# DATABASE MODELS
# =============================================
class Category(Base):
    __tablename__ = "store_category"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

class Product(Base):
    __tablename__ = "store_product"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, default=0)
    category_id = Column(Integer, ForeignKey("store_category.id"), default=1)
    description = Column(String(250), default="", nullable=True)
    image = Column(String(200), nullable=True)
    is_sale = Column(Boolean, default=False)
    sale_price = Column(Float, default=0)

class Customer(Base):
    __tablename__ = "store_customer"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone = Column(String(20), nullable=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))

class Order(Base):
    __tablename__ = "store_order"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("store_product.id"))
    customer_id = Column(Integer, ForeignKey("store_customer.id"))
    quantity = Column(Integer, default=1)
    address = Column(String(100), default="", nullable=True)
    phone = Column(String(20), default="", nullable=True)
    date = Column(Date, default=datetime.date.today)
    status = Column(Boolean, default=False)
    date_shipped = Column(DateTime, nullable=True)


# Create FastAPI app
app = FastAPI(
    title="E-commerce API Backend",
    description="A focused API for managing products and orders for the Django front-end.",
    version="2.0.0"
)

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/", response_model=MessageResponse)
def root():
    return {"message": "FastAPI E-commerce Backend is running"}


# =============================================
# PRODUCT ENDPOINTS (ALL INCLUDED)
# =============================================
@app.get("/products", response_model=List[ProductResponse], tags=["Products"])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products", response_model=ProductResponse, status_code=201, tags=["Products"])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.put("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        # If product doesn't exist, create it. This is an "upsert".
        new_product = Product(id=product_id, **product.dict())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product

    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}", response_model=MessageResponse, tags=["Products"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"message": f"Product {product_id} deleted successfully"}


# =============================================
# CUSTOMER ENDPOINTS
# =============================================
@app.get("/customers", response_model=List[CustomerResponse], tags=["Customers"])
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return customers

@app.post("/customers", response_model=CustomerResponse, status_code=201, tags=["Customers"])
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing:
        return existing
    
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


# =============================================
# HELPER FUNCTION (Used by Order Endpoints)
# =============================================
def enrich_order_details(order: Order, db: Session):
    product = db.query(Product).filter(Product.id == order.product_id).first()
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    
    if not product or not customer:
        return None
    
    price = product.sale_price if product.is_sale and product.sale_price > 0 else product.price
    amount_paid = float(price) * order.quantity
    
    return {
        "id": order.id,
        "full_name": f"{customer.first_name} {customer.last_name}".strip(),
        "email": customer.email,
        "shipping_address": order.address or "No address provided",
        "amount_paid": amount_paid,
        "date_ordered": order.date.strftime('%Y-%m-%d') if order.date else None,
        "shipped": order.status,
        "date_shipped": order.date_shipped.strftime('%Y-%m-%d %H:%M') if order.date_shipped else None,
        "items_list": [{
            "product": {"name": product.name},
            "quantity": order.quantity,
            "price": float(price)
        }]
    }


# =============================================
# ORDER ENDPOINTS
# =============================================
@app.get("/orders", response_model=List[DjangoOrderResponse], tags=["Orders"])
def get_all_orders(
    skip: int = 0, 
    limit: int = 100, 
    shipped: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Order).order_by(Order.id.desc())
    if shipped is not None:
        query = query.filter(Order.status == shipped)
    
    orders = query.offset(skip).limit(limit).all()
    
    response_list = [enrich_order_details(order, db) for order in orders]
    return [res for res in response_list if res is not None]

@app.get("/orders/{order_id}", response_model=DjangoOrderResponse, tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    enriched = enrich_order_details(order, db)
    if not enriched:
        raise HTTPException(status_code=404, detail="Associated product or customer not found for this order")
    
    return enriched

@app.post("/orders", response_model=OrderResponse, status_code=201, tags=["Orders"])
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {order.product_id} not found")
    
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    price = product.sale_price if product.is_sale and product.sale_price > 0 else product.price
    amount_paid = float(price) * db_order.quantity

    return OrderResponse(
        id=db_order.id, product_id=db_order.product_id, customer_id=db_order.customer_id,
        quantity=db_order.quantity, address=db_order.address, phone=db_order.phone,
        date_ordered=db_order.date.isoformat() if db_order.date else None,
        status=db_order.status, date_shipped=db_order.date_shipped.isoformat() if db_order.date_shipped else None,
        amount_paid=amount_paid, customer_email=customer.email
    )

@app.put("/orders/{order_id}", response_model=DjangoOrderResponse, tags=["Orders"])
def update_order(order_id: int, order: OrderUpdate, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    update_data = order.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "status":
            if value and not db_order.date_shipped:
                 db_order.date_shipped = datetime.datetime.now()
            elif not value:
                db_order.date_shipped = None
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    
    return enrich_order_details(db_order, db)

@app.delete("/orders/{order_id}", response_model=MessageResponse, tags=["Orders"])
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(db_order)
    db.commit()
    return {"message": f"Order {order_id} deleted successfully"}


# =============================================
# LEGACY ENDPOINTS
# =============================================
@app.get("/orders-shipped", response_model=List[DjangoOrderResponse], tags=["Legacy Orders"])
def get_orders_shipped(db: Session = Depends(get_db)):
    shipped_orders = db.query(Order).filter(Order.status == True).all()
    response = [enrich_order_details(order, db) for order in shipped_orders]
    return [res for res in response if res is not None]

@app.get("/orders-unshipped", response_model=List[DjangoOrderResponse], tags=["Legacy Orders"])
def get_orders_unshipped(db: Session = Depends(get_db)):
    unshipped_orders = db.query(Order).filter(Order.status == False).all()
    response = [enrich_order_details(order, db) for order in unshipped_orders]
    return [res for res in response if res is not None]


# =============================================
# ANALYSIS ENDPOINTS
# =============================================
@app.get("/analysis/revenue/{product_id}", response_model=ProductAnalysisResponse, tags=["Analysis"])
def get_total_revenue_per_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    orders = db.query(Order).filter(Order.product_id == product_id).all()
    total_revenue = 0.0
    total_quantity = 0
    for order in orders:
        price = product.sale_price if product.is_sale and product.sale_price > 0 else product.price
        total_revenue += order.quantity * price
        total_quantity += order.quantity
    return {"product_id": product_id, "product_name": product.name, "total_revenue": total_revenue, "total_quantity_sold": total_quantity}

@app.get("/analysis/highest-selling", response_model=ProductAnalysisResponse, tags=["Analysis"])
def get_highest_selling_product(db: Session = Depends(get_db)):
    top_selling = db.query(Order.product_id, func.sum(Order.quantity).label("total_quantity")).group_by(Order.product_id).order_by(func.sum(Order.quantity).desc()).first()
    if not top_selling:
        raise HTTPException(status_code=404, detail="No sales data found")
    product = db.query(Product).filter(Product.id == top_selling.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {top_selling.product_id} not found")
    orders = db.query(Order).filter(Order.product_id == product.id).all()
    total_revenue = 0.0
    for order in orders:
        price = product.sale_price if product.is_sale and product.sale_price > 0 else product.price
        total_revenue += order.quantity * price
    return {"product_id": product.id, "product_name": product.name, "total_revenue": total_revenue, "total_quantity_sold": top_selling.total_quantity}


# =============================================
# UTILITY ENDPOINT TO ADD DATA
# =============================================
@app.post("/create-sample-data", tags=["Utility"])
def create_sample_data(db: Session = Depends(get_db)):
    if db.query(Order).first():
        return {"message": "Sample data already exists."}

    sample_category = Category(name="Sample Category")
    db.add(sample_category)
    db.commit()
    db.refresh(sample_category)

    sample_customer = Customer(first_name="John", last_name="Doe", email="john.doe@example.com", password="password")
    db.add(sample_customer)
    db.commit()
    db.refresh(sample_customer)

    prod1 = Product(name="Sample Unshipped Product", price=29.99, category_id=sample_category.id)
    prod2 = Product(name="Sample Shipped Product", price=49.99, category_id=sample_category.id)
    db.add_all([prod1, prod2])
    db.commit()
    db.refresh(prod1)
    db.refresh(prod2)

    order1 = Order(product_id=prod1.id, customer_id=sample_customer.id, quantity=2, address="123 Main St", status=False)
    order2 = Order(product_id=prod2.id, customer_id=sample_customer.id, quantity=1, address="456 Oak Ave", status=True, date_shipped=datetime.datetime.now())
    db.add_all([order1, order2])
    db.commit()
    
    return {"message": "Sample data created successfully!"}


# =============================================
# ERROR HANDLERS
# =============================================
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Resource not found"})

@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# =============================================
# APP RUNNER
# =============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)