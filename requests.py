from sqlalchemy import select, update
from models import async_session, User, Order, Product
from pydantic import BaseModel, ConfigDict
from datetime import date
from decimal import Decimal
from typing import List, Optional
from schemas import ProductOut, OrderOut, UpdateProduct
from fastapi import HTTPException

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

async def update_product_data(product_data: UpdateProduct):
    async with async_session() as session:
        values = {
            "title": product_data.title,
            "category": product_data.category,
            "price": product_data.price,
            "size": product_data.size,
            "color": product_data.color,
            "quantity": product_data.quantity,
        }

        if product_data.image_url is not None:
            values["image_url"] = product_data.image_url

        stmt = (
            update(Product)
            .where(Product.id == product_data.id)
            .values(**values)
        )

        await session.execute(stmt)
        await session.commit()

async def update_product_quantity(product_id: int, new_quantity: int):
    # Логика для обновления количества товара в базе
    product = await db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.quantity = new_quantity
        await db.commit()  # Сохраняем изменения в базе
    else:
        raise ValueError("Product not found")

async def create_order(
    tg_id: int,
    items: list[OrderItem],
    shipping_address: str,
    city: str,
    payment_method: str,
    notes: str | None,
    timestamp: date | None,
    async_session: AsyncSession
) -> None:

    user = await add_user(tg_id)  #
    product_ids = [it.id for it in items]
    async with async_session() as session:

        result = await session.execute(select(Product).where(Product.id.in_(product_ids)))
        products = {p.id: p for p in result.scalars().all()}

        for it in items:
            prod = products.get(it.id)
            if not prod:
                raise HTTPException(404, f"Product {it.id} not found")
            if prod.quantity < it.quantity:
                raise HTTPException(400, f"Not enough stock for {prod.title}")

            prod.quantity -= it.quantity
            session.add(prod)  

        total_sum = sum(products[it.id].price * it.quantity for it in items)
        total_qty = sum(it.quantity for it in items)
        order_date = timestamp or date.today()

        new_order = Order(
            user=user.id,
            timestamp=order_date,
            order_sum=total_sum,
            shipping_address=shipping_address,
            city=city,
            payment_method=payment_method,
            quantity=total_qty,
            email=user.email or "",
            phone=user.phone or "",
            notes=notes
        )
        session.add(new_order)
        await session.flush()  

        for it in items:
            op = OrderProducts(
                order_id=new_order.id,
                product_id=it.id,
                quantity=it.quantity
            )
            session.add(op)
        await session.commit()
