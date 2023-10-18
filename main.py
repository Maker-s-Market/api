from typing import Union

import io

from fastapi import FastAPI, File
from starlette.responses import StreamingResponse
from routers import product, category

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
