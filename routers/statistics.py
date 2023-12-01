from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.JWTBearer import JWTBearer
from auth.auth import get_current_user, jwks
from db.database import get_db
from repositories.orderItemRepo import get_orders_items_by_product_id
from repositories.productRepo import get_products_by_user_id
from repositories.userRepo import get_user

auth = JWTBearer(jwks)
router = APIRouter(tags=['Statistics'])


@router.get("/statistics")
async def statistics(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
        Function that returns the statistics of the application
    """
    user = get_user(username, db)
    products_names = [product.name for product in get_products_by_user_id(user.id, db)]
    sales = {}
    for product_id in products_names:
        sales[product_id] = 0
        items = get_orders_items_by_product_id(product_id, db)
        for item in items:
            sales[product_id] += item.quantity
    return sales

