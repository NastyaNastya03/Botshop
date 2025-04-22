from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.order import OrderCreate, OrderOut
from app.services.order_service import OrderService
from app.models.db import get_async_session

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/{tg_id}", response_model=list[OrderOut])
async def get_orders_by_user(tg_id: int, db: AsyncSession = Depends(get_async_session)):
    return await get_user_orders(db, tg_id)

@router.post("/", response_model=OrderOut)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        return await OrderService(db).create_order(order_data)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.patch("/complete")
async def mark_order_completed(order: CompleteOrder, db: AsyncSession = Depends(get_async_session)):
    await complete_order(db, order.id)
    return {"status": "completed"}
