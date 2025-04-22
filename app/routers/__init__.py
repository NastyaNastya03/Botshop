from fastapi import APIRouter
from .admin import router as admin_router
from .order import router as order_router
from .upload import router as upload_router

router = APIRouter()
router.include_router(admin_router)
router.include_router(order_router)
router.include_router(upload_router)

__all__ = ["router"]
