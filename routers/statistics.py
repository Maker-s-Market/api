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
    products_id = [product.id for product in get_products_by_user_id(user.id, db)]
    sales = []
    total_quantity = 0
    total_views_products = 0
    for product_id in products_id:
        value = 0
        items = get_orders_items_by_product_id(product_id, db)
        for item in items:
            value += item.quantity
            total_quantity += item.quantity
        product = get_product_by_id(product_id, db)
        total_views_products += product.number_views
        sales.append({"name": product.name, "value": value})
    total_views_profile = user.views
    top_product_sale = max(sales, key=lambda x: x["value"])["name"] if sales else ""

    response = {"chart": sales,
                "statistics":
                    [
                        {"name": "Total Quantity", "value": total_quantity},
                        {"name": "Total Views Profile", "value": total_views_profile},
                        {"name": "Total Views Products", "value": total_views_products},
                        {"name": "Top Product Sale", "value": top_product_sale}
                    ]
                }
    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@router.get("/statistics/buyer", dependencies=[Depends(auth)])
async def statistics(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
        Function that returns the statistics of the buyer
    """

    user = get_user(username, db)
    orders = get_orders_by_user_id(user.id, db)

    if not orders:
        return JSONResponse(status_code=200, content=jsonable_encoder(create_empty_response()))
    return JSONResponse(status_code=200, content=jsonable_encoder(calculate_statistics(orders, db)))


def create_empty_response():
    response = {
        "statistics":
        [
            {"name": "Max Product", "value": ""},
            {"name": "Max Category", "value": ""},
            {"name": "Max Productor", "value": ""},
        ]
    }
    return response


def calculate_statistics(orders, db):
    quantity_per_product = {}
    quantity_per_category = {}
    quantity_per_productor = {}

    for order in orders:
        order_items = order.get_order_items(db)
        for item in order_items:
            product_id = item["product"]["id"]
            productor_id = item["product"]["user_id"]

            quantity_per_product[product_id] = quantity_per_product.get(product_id, 0) + item["quantity"]
            quantity_per_productor[productor_id] = quantity_per_productor.get(productor_id, 0) + item["quantity"]

            for category in item["product"]["categories"]:
                category_id = category["id"]
                quantity_per_category[category_id] = quantity_per_category.get(category_id, 0) + item["quantity"]

    max_product_id = max(quantity_per_product, key=quantity_per_product.get)
    max_productor_id = max(quantity_per_productor, key=quantity_per_productor.get)

    max_product = get_product_by_id(max_product_id, db)
    max_productor = get_user_by_id(max_productor_id, db)

    max_category = ""

    if quantity_per_category:
        max_category_id = max(quantity_per_category, key=quantity_per_category.get)
        max_category = get_category_by_id(max_category_id, db)

    return {
        "statistics":
        [
            {"name": "Max Product", "value": max_product.name},
            {"name": "Max Category", "value": max_category.name if max_category else ""},
            {"name": "Max Productor", "value": max_productor.username if max_productor else ""},
        ]
    }
