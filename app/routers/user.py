from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import add_user, check_admin_status
from app.models.base import get_async_session

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/{tg_id}")
async def get_or_create_user(tg_id: int, db: AsyncSession = Depends(get_async_session)):
    return await add_user(db, tg_id)

@router.get("/{tg_id}/is-admin")
async def check_admin(tg_id: int, db: AsyncSession = Depends(get_async_session)):
    return await check_admin_status(db, tg_id)
