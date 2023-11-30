
from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.order import CreateOrder
from models.orders.order import save_order as so

def save_order(order: CreateOrder, db: Session = Depends(get_db)):
    return so(order, db)