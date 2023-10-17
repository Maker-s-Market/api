from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from repositories.productRepo import *

from db.database import get_db

router = APIRouter(tags=['Product'])

@router.get("/product/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_product_by_id(product_id, db)


# @router.post("/product")
# async def create_product():
#     return {"message": "create product"}
#
#
# @router.put("/product")
# async def update_product():
#     return {"message": "update product"}
#
#
# @router.delete("/product")
# async def delete_product():
#     return {"message": "delete product"}
