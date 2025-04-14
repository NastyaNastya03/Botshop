from sqlalchemy import ForeignKey, String, BigInteger, Numeric, Date, Integer
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True) #уникальный индификатор 
    tg_id = mapped_column(BigInteger)                 #id по тг
    role: Mapped[str] = mapped_column(String(10))

class Product(Base):
    __tablename__ = 'products'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40))
    category: Mapped[str] = mapped_column(String(40))
    price = mapped_column(Numeric(10, 2))
    size: Mapped[int] = mapped_column(Integer)
    color: Mapped[str] = mapped_column(String(40))
    quantity: Mapped[int] = mapped_column(Integer)

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
    
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), primary_key=True)
    
class Admin(User):
    __tablename__ = 'admins'


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
