from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from models import get_async_session, init_db
import requests as rq
from schemas import CreateOrder, CreateProduct, CompleteOrder, CompleteProduct, ProductOut, OrderOut, UpdateProduct
import os
from typing import List
from admin import router as admin_router
from upload_products import router as upload_router
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        print('Database initialized')
        yield
    except Exception as e:
        print(f'Startup error: {e}')
        raise

app = FastAPI(title="To Do App", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://botminiapp-55dd0.web.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(admin_router)
app.include_router(upload_router)

# Keep-alive background task
async def keep_app_alive():
    while True:
        await asyncio.sleep(10)

@app.get("/")
async def root():
    return {"message": "Сервис работает"}

@app.get("/api/test-cors")
def test_cors():
    return {"status": "ok"}

# Пользователи
@app.get("/api/users/{tg_id}")
async def add_user_route(tg_id: int):
    user = await rq.add_user(tg_id)
    return user

@app.get("/api/is-admin/{tg_id}")
async def is_admin(tg_id: int):
    user = await rq.add_user(tg_id)
    return {"isAdmin": user.role == "admin"}

# Заказы
@app.get("/api/orders/{tg_id}", response_model=List[OrderOut])
async def get_user_orders(tg_id: int):
    user = await rq.add_user(tg_id)
    return await rq.get_orders(user.id)

@app.post("/api/order/create")
async def create_order_route(
    order: CreateOrder, 
    session: AsyncSession = Depends(get_async_session)
):
    await rq.create_order(
        tg_id=order.tg_id,
        items=order.items,
        shipping_address=order.shipping_address,
        city=order.city,
        payment_method=order.payment_method,
        notes=order.notes,
        timestamp=order.timestamp,
        session=session
    )
    return {"status": "ok"}

@app.patch("/api/order/completed")
async def complete_order_route(order: CompleteOrder):
    await rq.update_order(order.id)
    return {'status': 'ok'}

# Товары
@app.get("/api/products", response_model=List[ProductOut])
async def get_products_route():
    return await rq.get_all_products()

@app.post("/api/product/create")
async def create_product_route(product: CreateProduct):
    user = await rq.add_user(product.tg_id)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create products")

    await rq.create_product(
        title=product.title,
        category=product.category,
        price=product.price,
        size=product.size,
        color=product.color,
        quantity=product.quantity
    )
    return {'status': 'ok'}

@app.patch("/api/product/completed")
async def complete_product_route(product: CompleteProduct):
    user = await rq.add_user(product.tg_id)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    await rq.update_product_quantity(product.id, product.quantity)
    return {'status': 'ok'}

@app.patch("/api/product/update")
async def update_product_route(
    product: UpdateProduct, 
    session: AsyncSession = Depends(get_async_session)
):
    user = await rq.add_user(product.tg_id)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    
    await rq.update_product_data(product)
    return {"status": "updated"}

@app.get("/api/product/{product_id}", response_model=ProductOut)
async def get_product_route(product_id: int):
    products = await rq.get_all_products()
    for product in products:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.patch("/api/product/decrease/{product_id}")
async def decrease_quantity(
    product_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    await rq.decrease_product_quantity(product_id, session)
    return {"status": "quantity decreased"}

@app.patch("/api/product/increase/{product_id}", response_model=ProductOut)
async def increase_quantity(
    product_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        return await rq.increase_product_quantity(product_id, session)
    except HTTPException as he:
        raise he  # Пробрасываем HTTPException как есть
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.patch("/api/products/update-quantities")
async def bulk_update_quantities(
    updates: list[dict[str, int]],  # [{product_id: 1, change: +1}]
    session: AsyncSession = Depends(get_async_session)
):
    for update in updates:
        product = await session.get(Product, update["product_id"])
        product.quantity += update["change"]
    await session.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        workers=2,
        timeout_keep_alive=60
    )
