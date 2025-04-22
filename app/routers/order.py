from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.order import CreateOrder, OrderOut, CompleteOrder
from app.services.order_service import (
    create_order,
    get_user_orders,
    complete_order
)
from app.models.db import get_async_session

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.get("/{tg_id}", response_model=list[OrderOut])
async def get_orders_by_user(tg_id: int, db: AsyncSession = Depends(get_async_session)):
    return await get_user_orders(db, tg_id)

@router.post("/", status_code=201)
async def create_new_order(order: CreateOrder, db: AsyncSession = Depends(get_async_session)):
    await create_order(db, **order.model_dump())
    return {"status": "created"}

@router.patch("/complete")
async def mark_order_completed(order: CompleteOrder, db: AsyncSession = Depends(get_async_session)):
    await complete_order(db, order.id)
    return {"status": "completed"}
