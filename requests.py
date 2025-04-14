from sqlalchemy import select
from models import async_session, User, Order, Product
from pydantic import BaseModel, ConfigDict
from datetime import date
from decimal import Decimal
from typing import List, Optional
from schemas import ProductOut, OrderOut

class BaseModelWithConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)
   
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
  
async def add_user(tg_id) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return user
        
        new_user = User(tg_id=tg_id)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

async def get_orders(user) -> List[OrderOut]:
    async with async_session() as session:
        orders = await session.scalars(
            select(Order).where(Order.user == user, Order.completed == False)
        )
        return [OrderOut.model_validate(order) for order in orders]

async def get_all_products() -> List[ProductOut]:
    async with async_session() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        return [ProductOut.model_validate(p) for p in products]

async def create_order(
    user: int,
    timestamp: Optional[date],
    product_ids: List[int],
    shipping_address: str,
    city: str,
    payment_method: str,
    quantity: int,
    email: str,
    phone: str
) -> None:
    async with async_session() as session:
        result = await session.execute(select(Product).where(Product.id.in_(product_ids)))
        products = result.scalars().all()

        if not products:
            raise ValueError("Продукты не найдены")

        total_sum = sum([p.price for p in products])
        order_date = timestamp or date.today()

        new_order = Order(
            user=user,
            timestamp=order_date,
            products=products,
            order_sum=total_sum,
            shipping_address=shipping_address,
            city=city,
            payment_method=payment_method,
            quantity=quantity,
            email=email,
            phone=phone
        )
        session.add(new_order)
        await session.commit()

async def create_product(
    title: str,
    category: str,
    price: Decimal,
    size: int,
    color: str,
    quantity: int
) -> None:
    async with async_session() as session:
        new_product = Product(
            title=title,
            category=category,
            price=price,
            size=size,
            color=color,
            quantity=quantity
        )
        session.add(new_product)
        await session.commit()

async def update_order(order_id: int) -> None:
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        if order:
            order.completed = True
            await session.commit()

async def update_product(product_id: int) -> None:
    async with async_session() as session:
        product = await session.scalar(select(Product).where(Product.id == product_id))
        if product:
            product.quantity = 0
            await session.commit()