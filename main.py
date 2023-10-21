from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.create_database import create_tables
from routers import product, category


@asynccontextmanager
async def lifespan(app):
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(category.router)
app.include_router(product.router)


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
