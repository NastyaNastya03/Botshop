from datetime import date
from decimal import Decimal
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models import Order, OrderProducts
from app.schemas.order import OrderItem

async def get_orders(
    session: AsyncSession,
    user_id: int,
    completed: bool = False
) -> List[Order]:
    """Получение заказов пользователя"""
    result = await session.scalars(
        select(Order).where(Order.user == user_id, Order.completed == completed)
    )
    return result.all()

async def create_order(self, order_data: OrderCreate) -> OrderOut:
    """Создание нового заказа"""
    from app.services.user_service import add_user
    
    # 1) Получаем/создаем пользователя
    user = await add_user(session, tg_id)

    # 2) Читаем товары
    ids = [it.product_id for it in items]
    result = await session.execute(select(Product).where(Product.id.in_(ids)))
    products = {p.id: p for p in result.scalars().all()}

    # 3) Проверяем и уменьшаем остатки
    for it in items:
        prod = products.get(it.product_id)
        if not prod:
            raise HTTPException(404, f"Product {it.product_id} not found")
        if prod.quantity < it.quantity:
            raise HTTPException(400, f"Not enough stock for {prod.title}")
        prod.quantity -= it.quantity
        session.add(prod)

    # 4) Считаем сумму и кол-во
    total_sum = sum(products[it.product_id].price * it.quantity for it in items)
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
    await session.flush()

    # 6) Связываем order_products
    for it in items:
        session.add(
            OrderProducts(
                order_id=new_order.id,
                product_id=it.product_id,
                quantity=it.quantity
            )
        )

    await session.commit()
    return new_order

async def update_order(
    session: AsyncSession,
    order_id: int
) -> None:
    """Пометить заказ как выполненный"""
    order = await session.scalar(select(Order).where(Order.id == order_id))
    if order:
        order.completed = True
        await session.commit()
        pass
