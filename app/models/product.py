from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from decimal import Decimal
from .base import Base

class Product(Base):
    __tablename__ = 'products'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40))
    category: Mapped[str] = mapped_column(String(40))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    size: Mapped[int] = mapped_column(Integer)
    color: Mapped[str] = mapped_column(String(40))
    quantity: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
