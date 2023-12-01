from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from auth.JWTBearer import JWTBearer
from auth.auth import get_current_user, jwks
from db.database import get_db
from repositories.orderItemRepo import get_orders_items_by_product_id
from repositories.productRepo import get_products_by_user_id
from repositories.userRepo import get_user

auth = JWTBearer(jwks)
router = APIRouter(tags=['Statistics'])


@router.get("/statistics/seller", dependencies=[Depends(auth)])
async def statistics(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
        Function that returns the statistics of the seller
    """
    user = get_user(username, db)
    products_names = [product.name for product in get_products_by_user_id(user.id, db)]
    sales = {}
    total_quantity = 0
    total_views_profile = 0
    total_views_products = 0
    for product_id in products_names:
        sales[product_id] = 0
        items = get_orders_items_by_product_id(product_id, db)
        for item in items:
            sales[product_id] += item.quantity
            total_quantity += item.quantity
    response = {"grafico": sales, "total_quantity": total_quantity, "total_views_profile": total_views_profile,
                "total_views_products": total_views_products, "top_product": products_names[0]}
    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@router.get("/statistics/buyer", dependencies=[Depends(auth)])
async def statistics(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
        Function that returns the statistics of the buyer
    """
    pass

# products por categorias
# top my category
# productores com mais vendas nessa categoria
