import datetime
from uuid import uuid4

from fastapi import Depends
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Enum
from sqlalchemy.orm import Session

from db.database import Base, get_db
from models.orders.status import Status
from repositories.orderItemRepo import get_order_items_by_order_id
from repositories.historyOrderRepo import get_order_history_by_order_id
from schemas.order import CreateOrder


def random_uuid():
    return str(uuid4())


class Order(Base):
    __tablename__ = "order"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    total_price = Column(Float, index=True, default=0, nullable=False)
    total_quantity = Column(Integer, index=True, default=0, nullable=False)
    status = Column(Enum(Status), index=True, default="Accepted", nullable=False)
    created_at = Column(String(50), default=datetime.datetime.now(), nullable=False)
    updated_at = Column(String(50), default=datetime.datetime.now(), nullable=False)
    user_id = Column(String(50), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    def to_dict(self, db: Session = Depends(get_db)):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "total_price": self.total_price,
            "total_quantity": self.total_quantity,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "order_items": [item.to_dict(db=db) for item in get_order_items_by_order_id(self.id, db)],
            "order_history": [item.to_dict(db=db) for item in get_order_history_by_order_id(self.id, db)]
        }

    def get_order_items(self, db: Session = Depends(get_db)):
        return [item.to_dict(db=db) for item in get_order_items_by_order_id(self.id, db)]

    def get_order_history(self, db: Session = Depends(get_db)):
        return [item.to_dict(db=db) for item in get_order_history_by_order_id(self.id, db)]

    def change_order_status(self, status: str, db: Session = Depends(get_db)):
        self.status = status
        db.commit()
        db.refresh(self)
        return self


def save_order(order: CreateOrder, db: Session = Depends(get_db)):
    db_order = Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order
