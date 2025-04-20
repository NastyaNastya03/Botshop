from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import async_session, Product
import csv
from io import StringIO
from decimal import Decimal
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload-products")
async def upload_products(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл должен быть .csv")

    contents = await file.read()
    try:
        try:
            decoded = contents.decode('utf-8-sig')
        except UnicodeDecodeError:
            decoded = contents.decode('utf-8')
    
        reader = csv.DictReader(StringIO(decoded))
        products = []
    
        for row in reader:
            try:
                required_fields = ['title', 'category', 'price', 'size', 'color', 'quantity']
                for field in required_fields:
                    if field not in row or not row[field].strip():
                        raise HTTPException(status_code=400, detail=f"Отсутствует поле: {field}")

                product = Product(
                    title=row['title'],
                    category=row['category'],
                    price=Decimal(row['price'].strip()),
                    size=int(row['size']),
                    color=row['color'],
                    quantity=int(row['quantity']),
                    image_url=row.get('image_url') or None
                )
                products.append(product)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Ошибка в строке: {row} — {e}")
    
        async with async_session() as session:
            session: AsyncSession  # Подсветка в IDE
            session.add_all(products)
            await session.commit()
    
        return {"addedCount": len(products)}
    
    except Exception as e:
        logger.exception("Ошибка при загрузке CSV")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки CSV: {e}")
