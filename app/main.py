# Упрощенная и улучшенная версия
from fastapi import FastAPI
from app.core.config import settings
from app.routers import routers
from app.models.db import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None
)

# Подключаем все роутеры
for router in routers:
    app.include_router(router)
