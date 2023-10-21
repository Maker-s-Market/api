from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db.database import get_db
from repositories.categoryRepo import get_category_by_id
from repositories.productRepo import get_product_by_id, new_product, get_top_products_db, \
    get_products_by_filters
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
async def create_product(product: CreateProduct,
                         db: Session = Depends(get_db)):
    return JSONResponse(status_code=201, content=jsonable_encoder(new_product(db=db, product=product).to_dict()))


@router.put("/product/{product_id}")
async def update_product(product_id: str, edit_product: CreateProduct, db: Session = Depends(get_db)):
    # TODO : AFTER TO IMPLEMENT THE USER and auth (only the owner can edit the product)
    product = get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=404, detail=MESSAGE_NOT_FOUND)
    product_response = product.update_product(db=db, product=edit_product)
    return JSONResponse(status_code=200, content=jsonable_encoder(product_response.to_dict()))


@router.delete("/product/{product_id}")
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    # TODO : AFTER TO IMPLEMENT THE USER and auth (only the owner can delete the product)
    product = get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=404, detail=MESSAGE_NOT_FOUND)
    product.delete(db=db)
    return JSONResponse(status_code=200, content=jsonable_encoder({"message": "Product deleted"}))


@router.get("/products")
async def get_products(q: str = "", limit: int = 10,
                       price_min: int = 0, price_max: int = 100000000,
                       sort: str = "newest", discount: bool = False,
                       category_id: str = None, db: Session = Depends(get_db)):
    # location: str = None, # TODO: AFTER TO IMPLEMENT THE USER and auth

    if category_id is not None and not get_category_by_id(category_id, db):
        raise HTTPException(status_code=404, detail="Category not found")

    if price_max is not None and price_min is not None and price_max < price_min:
        raise HTTPException(status_code=400, detail="Invalid price range")

    result = get_products_by_filters(q=q, limit=limit, price_min=price_min, price_max=price_max,
                                     discount=discount, sort=sort, category_id=category_id, db=db)

    return JSONResponse(status_code=200,
                        content=jsonable_encoder([product.to_dict() for product in result]))


@router.get("/top/product")
async def get_top_products(db: Session = Depends(get_db)):
    return JSONResponse(status_code=200, content=jsonable_encoder([product.to_dict()
                                                                   for product in get_top_products_db(db=db)]))
