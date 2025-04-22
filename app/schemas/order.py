from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal

class CreateOrder(BaseModel):
    tg_id: int
    items: List[OrderItem]
    quantity: int
    shipping_address: str
    city: str
    payment_method: str
    notes: Optional[str] = None
    timestamp: Optional[date] = None

class CompleteOrder(BaseModel):
    id: int

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
