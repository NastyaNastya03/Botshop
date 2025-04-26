from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession  
from models import async_session, User, Order, Product, OrderProducts  
from datetime import date
from decimal import Decimal
from typing import List, Optional
from schemas import ProductOut, OrderOut, UpdateProduct, OrderItem
from fastapi import HTTPException


#Пользователи
async def add_user(tg_id) -> User:
    async with async_session() as session:
        stmt = select(User).where(User.tg_id == tg_id)
        user = await session.scalar(stmt)
        if user:
            return user
        
        new_user = User(tg_id=tg_id, role='user')  # Явно указываем обязательные поля
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
#Товары
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
    async with async_session() as session:
        product = await session.scalar(select(Product).where(Product.id == product_id))
        if not product:
            raise HTTPException(404, "Product not found")
        product.quantity = new_quantity
        await session.commit()
        
async def increase_product_quantity(product_id: int, session: AsyncSession) -> ProductOut:
    """Увеличивает количество товара на 1 и возвращает обновлённый объект"""
    product = await session.scalar(select(Product).where(Product.id == product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.quantity += 1
    await session.commit()
    await session.refresh(product)  # Обновляем объект из БД
    return ProductOut.model_validate(product)


async def decrease_product_quantity(product_id: int, session: AsyncSession):
    """Уменьшает количество товара на 1 (но не ниже 1)"""
    product = await session.scalar(select(Product).where(Product.id == product_id))
    if not product:
        raise HTTPException(404, "Product not found")
    if product.quantity <= product.min_quantity:
        raise HTTPException(400, f"Cannot decrease below minimum quantity {product.min_quantity}")
    
    product.quantity -= 1
    await session.commit()

#Заказы        
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
    session: AsyncSession
) -> None:
    user = await add_user(tg_id)

    ids = [it.id for it in items]
    result = await session.execute(select(Product).where(Product.id.in_(ids)))
    products = {p.id: p for p in result.scalars().all()}

    for it in items:
        prod = products.get(it.id)
        if not prod:
            raise HTTPException(404, f"Product {it.id} not found")
        new_quantity = prod.quantity - it.quantity
        if new_quantity < 0:
            raise HTTPException(400, f"Not enough stock for {prod.title}. Available: {prod.quantity}")
            
        if new_quantity < prod.min_quantity:
            raise HTTPException(400, 
                f"Cannot order {it.quantity} items. Would breach minimum stock {prod.min_quantity}. "
                f"Max available: {prod.quantity - prod.min_quantity}"
            )
        
        prod.quantity = new_quantity
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
        session.add(
            OrderProducts(
                order_id=new_order.id,
                product_id=it.id,
                quantity=it.quantity
            )
        )
    await session.commit() 
