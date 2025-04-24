from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class BaseModelWithConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class OrderItem(BaseModel):
    id: int
    quantity: int
    
class CreateOrder(BaseModel):
    tg_id: int
    items: List[OrderItem]
    quantity: int
    shopping_address: str
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

class OrderOut(BaseModel):
    id: int
    user: int
    timestamp: date
    products: List[ProductOut]
    order_sum: Decimal
    shopping_address: str
    city: str
    payment_method: str
    quantity: int
    email: str
    phone: str
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
    
class OrderSchema(BaseModelWithConfig):
    id: int
    user: int
    timestamp: date
    products: List[ProductSchema]
    order_sum: Decimal
    shipping_address: str
    city: str
    payment_method: str
    quantity: int
    email: str
    phone: str
