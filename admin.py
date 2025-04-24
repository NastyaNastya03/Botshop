from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import get_async_session, User
import requests as rq

router = APIRouter(prefix="/admin")

@router.get("/check-admin/{tg_id}")
async def check_admin(
    tg_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    user = await rq.add_user(tg_id)
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Not an admin")
    return {"isAdmin": True}
