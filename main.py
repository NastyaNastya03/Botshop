from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from typing import List
from admin import router as admin_router

from models import init_db
import requests as rq
from schemas import CreateOrder, CreateProduct, CompleteOrder, CompleteProduct, ProductOut, OrderOut, UpdateProduct

@asynccontextmanager
async def lifespan(app_: FastAPI):
    await init_db()
    print('Bot is ready')
    yield

app = FastAPI(title="To Do App", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://botminiapp-55dd0.web.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(admin_router)

@app.get("/api/test-cors")
def test_cors():
    return {"status": "ok"}

@app.get("/api/users/{tg_id}")
async def add_user_route(tg_id: int):
    user = await rq.add_user(tg_id)
    return user

@app.get("/api/orders/{tg_id}", response_model=List[OrderOut])
async def get_user_orders(tg_id: int):
    user = await rq.add_user(tg_id)
    return await rq.get_orders(user.id)

@app.get("/api/products", response_model=List[ProductOut])
async def get_products():
    return await rq.get_all_products()

@app.get("/api/is-admin/{tg_id}")
async def is_admin(tg_id: int):
    user = await rq.add_user(tg_id)
    if user.role == "admin":
        return {"isAdmin": True}
    return {"isAdmin": False}

@app.post("/api/order/create")
async def create_order(order: CreateOrder):
    user = await rq.add_user(order.tg_id)
    try:
        await rq.create_order(
            user=user.id,
            timestamp=order.timestamp or date.today(),
            product_ids=order.product_ids,
            shipping_address=order.shipping_address,
            city=order.city,
            payment_method=order.payment_method,
            quantity=order.quantity,
            email="example@example.com",  # можно сделать order.email в будущем
            phone="79998887766"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}

@app.post("/api/product/create")
async def create_product(product: CreateProduct):
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

@app.patch("/api/order/completed")
async def complete_order(order: CompleteOrder):
    await rq.update_order(order.id)
    return {'status': 'ok'}

@app.patch("/api/product/completed")
async def complete_product(product: CompleteProduct):
    user = await rq.add_user(product.tg_id)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    await rq.update_product(product.id)
    return {'status': 'ok'}

@app.patch("/api/product/update")
async def update_product(product: UpdateProduct = Body(...)):
    user = await rq.add_user(product.tg_id)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    
    await rq.update_product_data(product)
    return {"status": "updated"}

@app.get("/api/product/{product_id}", response_model=ProductOut)
async def get_product(product_id: int):
    async with async_session() as session:
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductOut.model_validate(product)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",  # имя файла:имя переменной с FastAPI
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )


