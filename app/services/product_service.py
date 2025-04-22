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
