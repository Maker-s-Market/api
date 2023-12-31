import asyncio
import json
import os
import boto3
from typing import List
import resend

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from auth.JWTBearer import JWTBearer
from auth.auth import jwks, get_current_user
from db.database import get_db
from models.orders.history_order import create_history_order
from models.orders.order_item import save_order_item
from models.orders.status import Status
from repositories.orderItemRepo import get_orders_items_by_product_id
from repositories.orderRepo import save_order, get_orders_by_user_id_filter, get_order_by_id as get_order_id
from repositories.productRepo import get_product_by_id, get_products_by_user_id
from repositories.userRepo import get_user, get_user_by_id
from schemas.order import CreateOrder
from schemas.orderItem import CreateOrderItem

auth = JWTBearer(jwks)

router = APIRouter(tags=['Order'])

env_path = os.path.join(os.path.dirname(__file__), "..", '.aws')
load_dotenv(env_path)

AWS_REGION = os.environ.get("AWS_REGION")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
API_KEY_EMAIL = os.environ.get("API_KEY_EMAIL")
resend.api_key = API_KEY_EMAIL

client = boto3.client(
    'lambda',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


async def invoke(order):
    client.invoke(
        FunctionName='lambda_func',
        InvocationType='Event',
        Payload=json.dumps({"order_id": order.id})
    )


async def send_email(email, message):
    params = {
        "from": "Makers Market <helpdesk@makers-market.pt>",
        "to": [email],
        "subject": "Order status changed",
        "text": message,
        "html": "<p>" + message + "</p>"
    }

    email = resend.Emails.send(params)
    print(email)


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
        total_quantity += item.quantity
        total_price += ((product.price * (100 - product.discount)*0.01) * item.quantity)

    order = CreateOrder(user_id=user.id, total_price=total_price, total_quantity=total_quantity)
    order_db = save_order(order, db)

    for item in products:
        save_order_item(item, order_db.id, db)

    create_history_order("Accepted", order_db.id, db)
    order_db.change_order_status("Accepted", db)

    await invoke(order_db)
    await send_email(user.email, "Your order has been accepted.")

    return JSONResponse(status_code=201, content=jsonable_encoder(order_db.to_dict(db=db)))


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
    if sort is None:
        sort = "desc_date"
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


@router.put("/order/{order_id}/status")
async def change_order_status(order_id: str, status: str, db: Session = Depends(get_db)):
    order = get_order_id(order_id, db)
    if order is None:
        detail = "Order with id: " + order_id + " was not found."
        raise HTTPException(status_code=404, detail=detail)
    if status == order.status:
        detail = "Order already has status " + status + "."
        raise HTTPException(status_code=400, detail=detail)
    if status not in Status.__members__:
        detail = "Status " + status + " is not valid."
        raise HTTPException(status_code=400, detail=detail)
    create_history_order(status, order_id, db)
    order.change_order_status(status, db)
    user = get_user_by_id(order.user_id, db)

    await send_email(user.email, "Your order status has been changed to " + status + ".")

    return JSONResponse(status_code=200, content=jsonable_encoder(order.to_dict(db=db)))
