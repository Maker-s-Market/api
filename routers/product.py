from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from repositories.productRepo import get_product_by_id, new_product

from db.database import get_db
from schemas.product import CreateProduct

router = APIRouter(tags=['Product'])


@router.get("/product/{product_id}")
async def get_product(product_id: str, db: Session = Depends(get_db)):
    product = get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.increment_number_views(db=db)
    return JSONResponse(status_code=200, content=jsonable_encoder(product.to_dict()))


@router.post("/product")
async def create_product(product: CreateProduct, db: Session = Depends(get_db)):
    return JSONResponse(status_code=201, content=jsonable_encoder(new_product(db=db, product=product).to_dict()))


@router.put("/product/{product_id}")
async def update_product(product_id: str, edit_product: CreateProduct, db: Session = Depends(get_db)):
    product = get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product_response = product.update_product(db=db, product=edit_product)
    return JSONResponse(status_code=200, content=jsonable_encoder(product_response.to_dict()))


@router.delete("/product{product_id}")
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    product = get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.delete(db=db)
    return JSONResponse(status_code=200, content=jsonable_encoder({"message": "Product deleted"}))
