import os
from typing import List

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from auth.JWTBearer import JWTBearer
from auth.auth import jwks, get_current_user
from db.database import get_db
from models.orders.order_item import save_order_item
from models.orders.status import Status
from repositories.orderItemRepo import get_orders_items_by_product_id
from repositories.orderRepo import save_order, get_orders_by_user_id_filter, get_order_by_id as get_order_id
from repositories.productRepo import get_product_by_id, get_products_by_user_id
from repositories.userRepo import get_user, get_user_by_id
from schemas.order import CreateOrder
from schemas.orderItem import CreateOrderItem
import stripe
env_path = os.path.join(os.path.dirname(__file__), "..", '.env')
load_dotenv(env_path)
stripe.api_key = os.getenv("STRIPE_KEY")

auth = JWTBearer(jwks)

router = APIRouter(tags=['Order'])


@router.post("/order", dependencies=[Depends(auth)])
async def create_order(products: List[CreateOrderItem], db: Session = Depends(get_db),
                       username: str = Depends(get_current_user)):
    user = get_user(username, db)

    total_price = 0
    total_quantity = 0
    for item in products:
        product = get_product_by_id(item.product_id, db)
        if product is None:
            detail = "Product with id: " + item.product_id + " was not found."
            raise HTTPException(status_code=404, detail=detail)
        if product.user_id == user.id:
            detail = "You can't buy your own product."
            raise HTTPException(status_code=400, detail=detail)
        if item.quantity <= 0:
            detail = "Quantity must be greater than 0."
            raise HTTPException(status_code=400, detail=detail)
        # TODO : quantidade em stock
        total_quantity += item.quantity
        total_price += ((product.price * (1 - product.discount)) * item.quantity)

    amount_in_cents = int(total_price * 100)

    payment = stripe.PaymentIntent.create(
        amount=amount_in_cents,
        currency="eur",
        payment_method_types=["card"],
        description="Order payment in MarkersMarket",
    )
    order = CreateOrder(user_id=user.id, total_price=total_price, total_quantity=total_quantity)
    order_db = save_order(order, db)

    for item in products:
        save_order_item(item, order_db.id, db)

    return JSONResponse(status_code=201,
                        content=jsonable_encoder({"order": order_db.to_dict(db=db),
                                                  "client_secret": payment.client_secret}))


@router.get("/order", dependencies=[Depends(auth)])
async def get_orders(status: str = None, sort: str = None, db: Session = Depends(get_db),
                     username: str = Depends(get_current_user)):
    if status not in Status.__members__ and status is not None:
        detail = "Status " + status + " is not valid."
        raise HTTPException(status_code=400, detail=detail)
    list_sort = ["desc_price", "asc_price", "desc_date", "asc_date", "desc_quantity", "asc_quantity"]

    if sort not in list_sort and sort is not None:
        detail = "Sort " + sort + " is not valid."
        raise HTTPException(status_code=400, detail=detail)

    user = get_user(username, db)
    orders = get_orders_by_user_id_filter(user_id=user.id, status=status, sort=sort, db=db)

    return JSONResponse(status_code=200, content=jsonable_encoder([order.to_dict(db=db) for order in orders]))


@router.get("/order/seller", dependencies=[Depends(auth)])
async def get_orders_seller(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """ which products of mine have been requested """
    user = get_user(username, db)
    products = get_products_by_user_id(user.id, db)
    orders_seller = []
    for product in products:
        order_items = get_orders_items_by_product_id(product.id, db)
        for item in order_items:
            order = get_order_id(item.order_id, db)
            buyer = get_user_by_id(order.user_id, db)

            orders_seller.append({
                "product": product.to_dict(),
                "buyer_name": buyer.name,
                "buyer_id": buyer.id,
                "quantity": item.quantity
            })
    return JSONResponse(status_code=200, content=jsonable_encoder(orders_seller))


@router.get("/order/{order_id}", dependencies=[Depends(auth)])
async def get_order_by_id(order_id: str, db: Session = Depends(get_db),
                          username: str = Depends(get_current_user)):
    user = get_user(username, db)
    order = get_order_id(order_id, db)
    if order is None:
        detail = "Order with id: " + order_id + " was not found."
        raise HTTPException(status_code=404, detail=detail)
    print(order.user_id)
    if order.user_id != user.id:
        detail = "You don't have permission to access this order."
        raise HTTPException(status_code=403, detail=detail)
    return JSONResponse(status_code=200, content=jsonable_encoder(order.to_dict(db=db)))
