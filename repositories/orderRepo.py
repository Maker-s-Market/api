from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.order import CreateOrder
from models.orders.order import save_order as so, Order


def save_order(order: CreateOrder, db: Session = Depends(get_db)):
    return so(order, db)


def get_order_by_id(order_id: str, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.id == order_id).first()


def get_orders_by_user_id(user_id: str, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.user_id == user_id).all()


def get_orders_by_user_id_filter(user_id: str, status: str, sort: str, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.user_id == user_id)
    if status is not None:
        orders = orders.filter(Order.status == status)
    if sort is not None:
        if sort == "desc_date":
            orders = orders.order_by(Order.created_at)
        elif sort == "asc_date":
            orders = orders.order_by(Order.created_at.desc())
        elif sort == "desc_price":
            orders = orders.order_by(Order.total_price)
        elif sort == "asc_price":
            orders = orders.order_by(Order.total_price.desc())
        elif sort == "desc_quantity":
            orders = orders.order_by(Order.total_quantity)
        elif sort == "asc_quantity":
            orders = orders.order_by(Order.total_quantity.desc())
    return orders.all()
