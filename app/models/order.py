from sqlalchemy import ForeignKey, Numeric, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base
from .product import Product
from .user import User
from typing import List

class Order(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int] = mapped_column(ForeignKey('users.id'))
    timestamp: Mapped[Date] = mapped_column()
    products: Mapped[List[Product]] = relationship("Product", secondary="order_products")
    order_sum: Mapped[Numeric(10, 2)] = mapped_column()
    completed: Mapped[bool] = mapped_column(default=False)
    shipping_address: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    payment_method: Mapped[str] = mapped_column(String(50))
    quantity: Mapped[int] = mapped_column(Integer)
    email: Mapped[str] = mapped_column(String(128))
    phone: Mapped[str] = mapped_column(String(12))

class OrderProducts(Base):
    __tablename__ = 'order_products'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity: Mapped[int] = mapped_column(Integer)
