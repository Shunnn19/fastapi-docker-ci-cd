# =============================================
# FILE: schemas.py - Pydantic Models for FastAPI
# =============================================

from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import date, datetime

# =============================================
# BASE SCHEMAS
# =============================================

class MessageResponse(BaseModel):
    message: str

# =============================================
# CATEGORY SCHEMAS
# =============================================

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# =============================================
# PRODUCT SCHEMAS
# =============================================

class ProductBase(BaseModel):
    name: str
    price: float = 0.0
    category_id: int = 1
    description: Optional[str] = ""
    image: Optional[str] = None
    is_sale: bool = False
    sale_price: float = 0.0

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    image: Optional[str] = None
    is_sale: Optional[bool] = None
    sale_price: Optional[float] = None

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

# =============================================
# CUSTOMER SCHEMAS
# =============================================

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: EmailStr
    password: str

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: str

    class Config:
        from_attributes = True

# =============================================
# ORDER SCHEMAS
# =============================================

class OrderBase(BaseModel):
    product_id: int
    customer_id: int
    quantity: int = 1
    address: Optional[str] = ""
    phone: Optional[str] = ""

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    product_id: Optional[int] = None
    customer_id: Optional[int] = None
    quantity: Optional[int] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[bool] = None

class OrderResponse(BaseModel):
    id: int
    product_id: int
    customer_id: int
    quantity: int
    address: Optional[str] = None
    phone: Optional[str] = None
    date_ordered: Optional[str] = None
    status: bool
    date_shipped: Optional[str] = None
    amount_paid: float
    customer_email: str

    class Config:
        from_attributes = True

# =============================================
# TEMPLATE-COMPATIBLE SCHEMAS (LEGACY)
# =============================================

class TemplateOrderResponse(BaseModel):
    """Schema that matches the format expected by Django templates"""
    id: int
    amount_paid: float
    email: str
    date_ordered: Optional[str] = None
    date_shipped: Optional[str] = None
    shipped: bool

    class Config:
        from_attributes = True

# =============================================
# DJANGO-COMPATIBLE SCHEMAS
# =============================================

class OrderItem(BaseModel):
    """Individual item in an order"""
    product: Dict[str, Any]
    quantity: int
    price: float

class DjangoOrderResponse(BaseModel):
    """Schema that matches Django payment.models.Order format"""
    id: int
    full_name: str
    email: str
    shipping_address: str
    amount_paid: float
    date_ordered: Optional[str] = None
    shipped: bool
    date_shipped: Optional[str] = None
    items_list: List[OrderItem] = []

    class Config:
        from_attributes = True

# =============================================
# UTILITY SCHEMAS
# =============================================

class ShippingStatusUpdate(BaseModel):
    shipped: bool

class OrderUpdateResponse(BaseModel):
    message: str
    shipped: bool
    order_id: int

    class Config:
        from_attributes = True

# =============================================
# SEARCH AND FILTER SCHEMAS
# =============================================

class ProductFilter(BaseModel):
    category_id: Optional[int] = None
    is_sale: Optional[bool] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search: Optional[str] = None

class OrderFilter(BaseModel):
    customer_id: Optional[int] = None
    product_id: Optional[int] = None
    status: Optional[bool] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None

# =============================================
# BULK OPERATION SCHEMAS
# =============================================

class BulkOrderUpdate(BaseModel):
    order_ids: List[int]
    status: bool

class BulkOrderResponse(BaseModel):
    updated_count: int
    message: str
    order_ids: List[int]

# =============================================
# STATISTICS SCHEMAS
# =============================================

class DatabaseStats(BaseModel):
    total_products: int
    total_customers: int
    total_orders: int
    shipped_orders: int
    pending_orders: int
    total_categories: int

class SalesStats(BaseModel):
    total_revenue: float
    orders_today: int
    orders_this_month: int
    top_selling_products: List[Dict[str, Any]]

# =============================================
# ERROR SCHEMAS
# =============================================

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    detail: List[Dict[str, Any]]
    error_type: str = "validation_error"