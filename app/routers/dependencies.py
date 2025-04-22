from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import get_async_session

async def get_db() -> AsyncSession:
    async for session in get_async_session():
        yield session
