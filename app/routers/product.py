from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.product import ProductOut, CreateProduct, UpdateProduct, CompleteProduct
from app.services.product_service import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product_data,
    complete_product
)
from app.models.db import get_async_session

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("/", response_model=list[ProductOut])
async def list_products(db: AsyncSession = Depends(get_async_session)):
    return await get_all_products(db)

@router.get("/{product_id}", response_model=ProductOut)
async def get_product_details(product_id: int, db: AsyncSession = Depends(get_async_session)):
    product = await get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product

@router.post("/", status_code=201)
async def add_new_product(product: CreateProduct, db: AsyncSession = Depends(get_async_session)):
    await create_product(db, **product.model_dump())
    return {"status": "created"}

@router.patch("/complete")
async def mark_product_completed(product: CompleteProduct, db: AsyncSession = Depends(get_async_session)):
    await complete_product(db, product.id)
    return {"status": "completed"}

@router.patch("/update")
async def update_product_info(product: UpdateProduct, db: AsyncSession = Depends(get_async_session)):
    await update_product_data(db, product)
    return {"status": "updated"}
    
@router.post("/", response_model=ProductOut)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        product = await ProductService.create(db, product_data, current_user)
        return product
    except PermissionError as e:
        raise HTTPException(403, str(e))
