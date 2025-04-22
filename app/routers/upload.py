from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from .dependencies import get_db
import csv
from io import StringIO
from decimal import Decimal

router = APIRouter()

# Вспомогательная функция для обработки CSV
async def process_csv(contents: bytes) -> list:
    try:
        decoded = contents.decode('utf-8-sig')  # пробуем сначала utf-8-sig, потом utf-8
    except UnicodeDecodeError:
        decoded = contents.decode('utf-8')

    # Автоопределение разделителя
    sample = decoded[:1024]
    delimiter = ';' if sample.count(';') > sample.count(',') else ','

    reader = csv.DictReader(StringIO(decoded), delimiter=delimiter)
    required_fields = ['title', 'category', 'price', 'size', 'color', 'quantity']

    products = []
    for row in reader:
        try:
            # Проверка наличия обязательных полей
            for field in required_fields:
                if not row.get(field):
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
    
    return products


@router.post("/upload-products")
async def upload_products(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл должен быть .csv")

    contents = await file.read()

    try:
        # Обрабатываем содержимое CSV
        products = await process_csv(contents)

        # Работаем с базой данных и добавляем продукты
        async with async_session() as session:
            session: AsyncSession
            session.add_all(products)
            await session.commit()

        return {"addedCount": len(products)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки CSV: {e}")

        return {"addedCount": len(products)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки CSV: {e}")

