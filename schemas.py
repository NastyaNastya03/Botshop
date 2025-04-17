from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal

class CreateOrder(BaseModel):
    tg_id: int
    product_ids: List[int]
    quantity: int
    shipping_address: str
    city: str
    payment_method: str
    notes: Optional[str] = None
    timestamp: Optional[date] = None

class CreateProduct(BaseModel):
    tg_id: int
    title: str
    category: str
    price: Decimal
    size: int
    color: str
    quantity: int
    image_url: Optional[str]
    

class CompleteOrder(BaseModel):
    id: int

class CompleteProduct(BaseModel):
    id: int

class UpdateProduct(BaseModel):
    id: int
    title: str
    category: str
    price: float
    size: int
    color: str
    quantity: int
    image_url: Optional[str] = None
    tg_id: int



class ProductOut(BaseModel):
    id: int
    title: str
    category: str
    price: Decimal
    size: int
    color: str
    quantity: int
    image_url: Optional[str] = None
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    user: int
    timestamp: date
    products: List[ProductOut]
    order_sum: Decimal
    shipping_address: str
    city: str
    payment_method: str
    quantity: int
    email: str
    phone: str
    class Config:
        from_attributes = True
