from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal
from .base import BaseModelWithConfig

class CreateProduct(BaseModel):
    tg_id: int
    title: str
    category: str
    price: Decimal
    size: int
    color: str
    quantity: int
    image_url: Optional[str]
    
class CompleteProduct(BaseModel):
    id: int

class UpdateProduct(BaseModel):
    id: int
    title: str
    category: str
    price: Decimal
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

class ProductSchema(BaseModelWithConfig):
    id: int
    title: str
    category: str
    price: Decimal
    size: int
    color: str
    quantity: int

