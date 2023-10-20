from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from repositories.productRepo import get_product_by_id, new_product, get_all_products, get_top_products_db, \
    get_products_by_filters

from db.database import get_db
from schemas.product import CreateProduct

router = APIRouter(tags=['Product'])
MESSAGE_NOT_FOUND = "Product not found"


@router.get("/product/{product_id}")
async def get_product(product_id: str, db: Session = Depends(get_db)):
    product = get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=404, detail=MESSAGE_NOT_FOUND)
    product.increment_number_views(db=db)
    return JSONResponse(status_code=200, content=jsonable_encoder(product.to_dict()))


@router.post("/product")
async def create_product(product: CreateProduct, db: Session = Depends(get_db)):
    return JSONResponse(status_code=201, content=jsonable_encoder(new_product(db=db, product=product).to_dict()))


@router.put("/product/{product_id}")
async def update_product(product_id: str, edit_product: CreateProduct, db: Session = Depends(get_db)):
    product = get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=404, detail=MESSAGE_NOT_FOUND)
    product_response = product.update_product(db=db, product=edit_product)
    return JSONResponse(status_code=200, content=jsonable_encoder(product_response.to_dict()))


@router.delete("/product/{product_id}")
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    product = get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=404, detail=MESSAGE_NOT_FOUND)
    product.delete(db=db)
    return JSONResponse(status_code=200, content=jsonable_encoder({"message": "Product deleted"}))


@router.get("/products")
async def get_products(q: str = None,
                       limit: int = 10,
                       sort: str = "newest",
                       category: list = None,
                       price_min: int = None,
                       price_max: int = None,
                       discount: bool = None,
                       # location: str = None,
                       db: Session = Depends(get_db)):
    if category is None:
        category = []

    if sort not in ["newest", "oldest", "price_asc", "price_desc", "relevance"]:
        raise HTTPException(status_code=400, detail="Invalid sort parameter")

    if price_max is not None and price_min is not None and price_max < price_min:
        raise HTTPException(status_code=400, detail="Invalid price range")

    return JSONResponse(status_code=200, content=jsonable_encoder(
        [product.to_dict() for product in get_products_by_filters(q=q,
                                                                  price_min=price_min,
                                                                  price_max=price_max,
                                                                  limit=limit,
                                                                  db=db)]))


@router.get("/top/products")
async def get_top_products(db: Session = Depends(get_db)):
    return JSONResponse(status_code=200, content=jsonable_encoder([product.to_dict()
                                                                   for product in get_top_products_db(db=db)]))
