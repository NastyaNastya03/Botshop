from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import Admin, User
from .dependencies import get_db

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/check-admin/{tg_id}")
async def check_admin(
    tg_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, tg_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    is_admin = await db.get(Admin, user.id) is not None
    return {"isAdmin": is_admin}
