from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[BigInteger] = mapped_column()
    role: Mapped[str] = mapped_column(String(10))

class Admin(User):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
