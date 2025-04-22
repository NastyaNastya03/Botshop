from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from decimal import Decimal
from app.models.product import Product
from app.schemas.product import UpdateProduct

async def get_all_products(session: AsyncSession) -> list[Product]:
    """Получение всех товаров"""
    result = await session.execute(select(Product))
    return result.scalars().all()

async def create_product(
    session: AsyncSession,
    title: str,
    category: str,
    price: Decimal,
    size: int,
    color: str,
    quantity: int,
    image_url: str | None = None
) -> Product:
    """Создание нового товара"""
    new_product = Product(
        title=title,
        category=category,
        price=price,
        size=size,
        color=color,
        quantity=quantity,
        image_url=image_url
    )
    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)
    return new_product

async def update_product_data(
    session: AsyncSession,
    product_data: UpdateProduct
) -> None:
    """Обновление данных товара"""
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

async def update_product_quantity(
    session: AsyncSession,
    product_id: int,
    new_quantity: int
) -> None:
    """Обновление количества товара"""
    product = await session.scalar(select(Product).where(Product.id == product_id))
    if not product:
        raise HTTPException(404, "Product not found")
    product.quantity = new_quantity
    await session.commit()
