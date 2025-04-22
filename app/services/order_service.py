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

async def get_orders(user) -> List[OrderOut]:
    async with async_session() as session:
        orders = await session.scalars(
            select(Order).where(Order.user == user, Order.completed == False)
        )
        return [OrderOut.model_validate(order) for order in orders]

async def update_order(order_id: int) -> None:
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        if order:
            order.completed = True
            await session.commit()

async def create_order(
    tg_id: int,
    items: list[OrderItem],
    shipping_address: str,
    city: str,
    payment_method: str,
    notes: str | None,
    timestamp: date | None,
    session: AsyncSession       # <- вот сюда придёт готовая сессия из Depends
) -> None:
    # 1) Получаем/создаем пользователя
    user = await add_user(tg_id)

    # 2) Читаем товары
    ids = [it.id for it in items]
    result = await session.execute(select(Product).where(Product.id.in_(ids)))
    products = {p.id: p for p in result.scalars().all()}

    # 3) Проверяем и уменьшаем остатки
    for it in items:
        prod = products.get(it.id)
        if not prod:
            raise HTTPException(404, f"Product {it.id} not found")
        if prod.quantity < it.quantity:
            raise HTTPException(400, f"Not enough stock for {prod.title}")
        prod.quantity -= it.quantity
        session.add(prod)

    # 4) Считаем сумму и кол-во
    total_sum = sum(products[it.id].price * it.quantity for it in items)
    total_qty = sum(it.quantity for it in items)
    order_date = timestamp or date.today()

    # 5) Создаем заказ
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
    await session.flush()  # получаем new_order.id

    # 6) Связываем order_products
    for it in items:
        session.add(
            OrderProducts(
                order_id=new_order.id,
                product_id=it.id,
                quantity=it.quantity
            )
        )

    # 7) Финальный коммит
    await session.commit()
