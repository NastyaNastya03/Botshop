from contextlib import asynccontextmanager

from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from decimal import Decimal
from datetime import date

from models import init_db
import requests as rq


class CreateOrder(BaseModel):
    tg_id: int
    product_ids: List[int]
    quantity: int
    shipping_address: str
    city: str
    payment_method: str
    notes: Optional[str] = None
    timestamp:  Optional[date] = None
    

class CreateProduct(BaseModel):
    tg_id: int
    title: str
    category: str
    price: Decimal
    size: int
    color: str
    quantity: int
    
class CompleteOrder(BaseModel):
    id: int
    
class CompleteProduct(BaseModel):
    id: int
    
class ProductOut(BaseModel):
    id: int
    title: str
    category: str
    price: Decimal
    size: int
    color: str
    quantity: int
    
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



@asynccontextmanager
async def lifespan(app_: FastAPI):
    await init_db()
    print('Bot is ready')
    yield


app = FastAPI(title="To Do App", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/orders/{tg_id}",response_model=List[OrderOut]) #возвращаем заказы пользователя по тг id
async def get_user_orders(tg_id: int):
    user = await rq.add_user(tg_id)
    return await rq.get_orders(user.id) 

@app.get("/api/products", response_model=List[ProductOut])  
async def get_products():
    return await rq.get_all_products()  
    

@app.post("/api/order/create")
async def create_order(order: CreateOrder):
    user = await rq.add_user(order.tg_id)
    
    try:
        await rq.create_order(
            user=user.id,
            timestamp=order.timestamp or date.today(),
            product_ids=order.product_ids,
            shipping_address=order.shipping_address,
            city=order.city,
            payment_method=order.payment_method,
            quantity=order.quantity,
            email="example@example.com",  # можешь передавать в будущем из order.email
            phone="79998887766"           # можешь передавать в будущем из order.phone
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok"}


@app.post("/api/product/create")
async def create_product(product: CreateProduct):
    user = await rq.add_user(product.tg_id)
    
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create products")

    await rq.create_product(
        title=product.title,
        category=product.category,
        price=product.price,
        size=product.size,
        color=product.color,
        quantity=product.quantity
    )
    
    return {'status': 'ok'}


@app.patch("/api/order/completed")
async def complete_order(order: CompleteOrder):
    await rq.update_order(order.id)
    return {'status': 'ok'}

@app.patch("/api/product/completed")
async def complete_product(product: CompleteProduct):
    user = await rq.add_user(product.tg_id)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    await rq.update_product(product.id)
    return {'status': 'ok'}
