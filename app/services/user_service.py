from app.models import User, Admin

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


