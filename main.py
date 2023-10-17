from typing import Union

import io

from fastapi import FastAPI
from db.database import engine
from routers import product, category
from models.product import Product
from models.category import Category
from models.user import User
from models.rating import Rating
from models.review import Review
from models.wishList import WishList

User.metadata.create_all(bind=engine)
Product.metadata.create_all(bind=engine)
Category.metadata.create_all(bind=engine)
Rating.metadata.create_all(bind=engine)
Review.metadata.create_all(bind=engine)
WishList.metadata.create_all(bind=engine)


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
