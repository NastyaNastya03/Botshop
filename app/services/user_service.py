from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

async def add_user(session: AsyncSession, tg_id: int) -> User:
    """Добавляет нового пользователя или возвращает существующего"""
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        return user
    
    new_user = User(tg_id=tg_id)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


