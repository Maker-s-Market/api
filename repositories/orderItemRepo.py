from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from models.orders.order_item import OrderItem


def get_order_items_by_order_id(id_order: str, db: Session = Depends(get_db)):
    return db.query(OrderItem).filter(OrderItem.order_id == id_order).all()


def get_orders_items_by_product_id(id_product: str, db: Session = Depends(get_db)):
    return db.query(OrderItem).filter(OrderItem.product_id == id_product).all()