from sqlalchemy import ForeignKey, Integer, Numeric, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .product import Product
from decimal import Decimal

class Order(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int] = mapped_column(ForeignKey('users.id'))
    timestamp = mapped_column(Date)
    products: Mapped[list[Product]] = relationship("Product", secondary="order_products")
    order_sum = mapped_column(Numeric(10, 2))
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
