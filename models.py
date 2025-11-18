# =============================================
# FILE: models.py (FastAPI) - NOT USED IN CURRENT SETUP
# =============================================

# This file is not being used since models are now defined in main.py
# You can keep it for future use or delete it

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from database import Base
import datetime

class Category(Base):
    __tablename__ = "store_category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

class Product(Base):
    __tablename__ = "store_product"
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
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone = Column(String(20), nullable=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))

class Order(Base):
    __tablename__ = "store_order"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("store_product.id"))
    customer_id = Column(Integer, ForeignKey("store_customer.id"))
    quantity = Column(Integer, default=1)
    address = Column(String(100), default="", nullable=True)
    phone = Column(String(20), default="", nullable=True)
    date = Column(Date, default=datetime.date.today)
    status = Column(Boolean, default=False)
    date_shipped = Column(DateTime, nullable=True)