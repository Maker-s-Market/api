from typing import Union

import io

from fastapi import FastAPI, File
from starlette.responses import StreamingResponse
from db.database import engine, Base
from routers import product, category
from models.product import Product
from models.category import Category
from models.user import User

User.metadata.create_all(bind=engine)
Product.metadata.create_all(bind=engine)
Category.metadata.create_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(product.router)
app.include_router(category.router)


@app.get("/")
async def root():
    return {"message": "hello World!"}

# @app.post('/style')
# async def predict(img_bytes: bytes = File(...)):
#     img = io.BytesIO(img_bytes)
#     img.seek(0)
#     return StreamingResponse(
#         img,
#         media_type="image/jpg",
#     )
