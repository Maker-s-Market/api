from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from auth.JWTBearer import JWTBearer
from auth.auth import get_current_user, jwks
from db.database import get_db
from repositories.orderItemRepo import get_orders_items_by_product_id
from repositories.orderRepo import get_orders_by_user_id
from repositories.productRepo import get_products_by_user_id, get_product_by_id
from repositories.userRepo import get_user, get_user_by_id
from repositories.categoryRepo import get_category_by_id

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
    total_views_products = 0
    for product_id in products_names:
        sales[product_id] = 0
        items = get_orders_items_by_product_id(product_id, db)
        for item in items:
            sales[product_id] += item.quantity
            total_quantity += item.quantity

        total_views_products += get_product_by_id(product_id, db).views
    total_views_profile = 0  # TODO: IMPLEMENTAR
    top_product_sale = max(sales, key=lambda k: sales[k])

    response = {"chart": sales,
                "statistics":
                    {
                        "total quantity": total_quantity, "total views profile": total_views_profile,
                        "total views Products": total_views_products, "top product sale": products_names[0]
                    }
                }
    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@router.get("/statistics/buyer", dependencies=[Depends(auth)])
async def statistics(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
        Function that returns the statistics of the buyer
    """

    user = get_user(username, db)
    orders = get_orders_by_user_id(user.id, db)

    quantity_per_product = {}
    quantity_per_category = {}
    quantity_per_productor = {}

    for order in orders:
        order_items = order.get_order_items(db)
        for item in order_items:

            if item["product"]["id"] not in quantity_per_product.keys():
                quantity_per_product[item["product"]["id"]] = 0

            if item["product"]["user_id"] not in quantity_per_productor.keys():
                quantity_per_productor[item["product"]["user_id"]] = 0

            quantity_per_product[item["product"]["id"]] += item["quantity"]
            quantity_per_productor[item["product"]["user_id"]] += item["quantity"]

            for category in item["product"]["categories"]:
                if category["id"] not in quantity_per_category.keys():
                    quantity_per_category[category["id"]] = 0
                quantity_per_category[category["id"]] += item["quantity"]

    max_product = get_product_by_id(max(quantity_per_product, key=lambda k: quantity_per_product[k]), db)
    max_category = get_category_by_id(max(quantity_per_category, key=lambda k: quantity_per_category[k]), db)
    max_productor = get_user_by_id(max(quantity_per_productor, key=lambda k: quantity_per_productor[k]), db)

    response = {
        "max_product": max_product,
        "max_category": max_category,
        "max_productor": max_productor
    }

    return JSONResponse(status_code=200, content=jsonable_encoder(response))
