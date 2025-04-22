from fastapi import APIRouter

router = APIRouter()

@router.get("/check-admin/{tg_id}")
async def check_admin(tg_id: int):
    return {"isAdmin": True}
