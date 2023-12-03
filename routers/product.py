from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db.database import get_db
from repositories.categoryRepo import get_category_by_id
from repositories.productRepo import get_product_by_id, new_product, get_top_products_db, \
    get_products_by_filters
from repositories.userRepo import get_user, get_user_by_id
from schemas.product import CreateProduct, UpdateDiscount
from auth.JWTBearer import JWTBearer
from auth.auth import get_current_user, jwks

auth = JWTBearer(jwks)

router = APIRouter(tags=['Product'])
MESSAGE_NOT_FOUND = "Product not found"


@router.post("/product", dependencies=[Depends(auth)])
async def create_product(product: CreateProduct,
                         db: Session = Depends(get_db),
                         username: str = Depends(get_current_user)):
    return JSONResponse(status_code=201,
                        content=jsonable_encoder(new_product(db=db, product=product, username=username).to_dict()))


@router.put("/product/{product_id}", dependencies=[Depends(auth)])
async def update_product(product_id: str, edit_product: CreateProduct, db: Session = Depends(get_db),
                         username: str = Depends(get_current_user)):
    product = get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=404, detail=MESSAGE_NOT_FOUND)
    user = get_user(username, db)
    if user.id != product.user_id:
        raise HTTPException(status_code=403, detail="Only the user can change its products")
    product_response = product.update_product(db=db, product=edit_product)
    return JSONResponse(status_code=200, content=jsonable_encoder(product_response.to_dict()))


@router.delete("/product/{product_id}", dependencies=[Depends(auth)])
async def delete_product(product_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username, db)
    product = get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=404, detail=MESSAGE_NOT_FOUND)
    if user.id != product.user_id:
        raise HTTPException(status_code=403, detail="Only the user can change its products")
    product.delete(db=db)
    return JSONResponse(status_code=200, content=jsonable_encoder({"message": "Product deleted"}))


@router.get("/product")
async def get_products(q: str = "", limit: int = 10,
                       price_min: int = 0, price_max: int = 100000000,
                       sort: str = "newest", discount: bool = False, location: str = "",
                       category_id: str = "", db: Session = Depends(get_db)):
    if category_id != "" and not get_category_by_id(category_id, db):
        raise HTTPException(status_code=404, detail="Category not found")

    if price_max is not None and price_min is not None and price_max < price_min:
        raise HTTPException(status_code=400, detail="Invalid price range")

    result = get_products_by_filters(q=q, limit=limit, price_min=price_min, price_max=price_max,
                                     discount=discount, location=location, sort=sort, category_id=category_id, db=db)

    return JSONResponse(status_code=200,
                        content=jsonable_encoder([product.to_dict() for product in result]))


@router.get("/product/{product_id}")
async def get_product(product_id: str, db: Session = Depends(get_db)):
    product = get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=404, detail=MESSAGE_NOT_FOUND)
    user = get_user_by_id(product.user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if product.available is False:
        raise HTTPException(status_code=404, detail="Product not available")
    product.increment_number_views(db=db)
    response = {
        "product": product.to_dict(),
        "user": user.information()
    }
    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@router.get("/product/top/{limit}")
async def get_top_products(limit: int = 4, db: Session = Depends(get_db)):
    return JSONResponse(status_code=200, content=jsonable_encoder([product.to_dict()
                                                                   for product in get_top_products_db(limit=limit,
                                                                                                      db=db)]))


@router.put("/products/discount", dependencies=[Depends(auth)])
async def put_products_discount(update: UpdateDiscount, db: Session = Depends(get_db),
                                username: str = Depends(get_current_user)):
    """
        Create/Update a product discount
        # TODO: CANGHE THe name of this endpoint
    """
    product = get_product_by_id(product_id=update.product_id, db=db)
    user = get_user(username, db)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.user_id != user.id:
        raise HTTPException(status_code=403, detail="Only the user can change their product's discount")

    product.discount = update.discount
    updated_product = product.update_product(db, product)

    return JSONResponse(status_code=200, content=jsonable_encoder(updated_product.to_dict()))


@router.put("/products/{product_id}/available", dependencies=[Depends(auth)])
async def put_products_available(product_id: str, available: bool, db: Session = Depends(get_db),
                                 username: str = Depends(get_current_user)):
    """
    Change product available
    # TODO: CANGHE THe name of this endpoint
    """

    product = get_product_by_id(product_id=product_id, db=db)
    user = get_user(username, db)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.user_id != user.id:
        raise HTTPException(status_code=403, detail="Only the user can change their product's available")
    if product.available == available:
        raise HTTPException(status_code=400, detail="Product is already in that state")

    product.change_available(db=db)
    return JSONResponse(status_code=200, content=jsonable_encoder(product.to_dict()))
