from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from models.orders.history_order import HistoryOrder


def get_order_history_by_order_id(order_id: str, db: Session = Depends(get_db)):
    return db.query(HistoryOrder).filter(HistoryOrder.order_id == order_id).all()
