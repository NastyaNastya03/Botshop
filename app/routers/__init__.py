from .user import router as user_router
from .product import router as product_router
from .order import router as order_router
from .healthcheck import router as healthcheck_router
from .admin import router as admin_router
from .upload import router as upload_router

routers = [
    user_router,
    product_router,
    order_router,
    healthcheck_router,
    admin_router,
    upload_router
]
