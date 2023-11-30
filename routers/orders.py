from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from auth.auth import jwks, get_current_user
from auth.JWTBearer import JWTBearer
from db.database import get_db
from models.orders.order_item import save_order_item
from repositories.orderRepo import save_order
from repositories.productRepo import get_product_by_id
from repositories.userRepo import get_user
from schemas.order import CreateOrder
from schemas.orderItem import CreateOrderItem

auth = JWTBearer(jwks)

router = APIRouter(tags=['Product'])

@router.post("/order/place-order", dependencies=[Depends(auth)])
async def place_order(products: List[CreateOrderItem], db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username, db)
    #create order
    user_id = user.id
    total_price = 0
    total_quantity = 0
    for item in products:
        product = get_product_by_id(item.product_id)
        if product is None:
            detail = "Product with id: " + item.product_id + " was not found."
            raise HTTPException(status_code=404, detail=detail)
        total_quantity += item.quantity
        total_price += (product.price * (1-product.discount))

    #save order
    order = CreateOrder(user_id = user.id, total_price = total_price, total_quantity=total_quantity, order_items= products)
    order_db = save_order(order)

    for item in products:
        save_order_item(item, order_db.id, db)
    
    return JSONResponse(status_code=201, content=order_db.to_dict())