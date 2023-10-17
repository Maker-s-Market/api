from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from repositories.productRepo import new_product
from schemas.product import CreateProduct

router = APIRouter(tags=['Product'])

# @router.get("/product")
# async def get_product():
#     return {"message": "get product"}


@router.post("/product")
async def create_product(product: CreateProduct, db: Session = Depends(get_db)):
    return new_product(db=db, product=product)


# @router.put("/product")
# async def update_product():
#     return {"message": "update product"}
#
#
# @router.delete("/product")
# async def delete_product():
#     return {"message": "delete product"}
