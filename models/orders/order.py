import datetime
from uuid import uuid4
from fastapi import Depends, HTTPException

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, Session
from typing import List
from models.orders.order_item import OrderItem

from db.database import Base, get_db
from schemas.order import CreateOrder


def random_uuid():
    return str(uuid4())

# status : in_ progress, Shipped, Delivered, Cancelled, Rejected
class Order(Base):
    __tablename__ = "order"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    user_id = Column(String(50), ForeignKey('user.id'))
    total_price = Column(Float, index=True, default=0, nullable=False)
    total_quantity = Column(Integer, index=True, default=0, nullable=False)
    status = Column(String(50), index=True, default="in_progress", nullable=False)
    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)
    order_items = relationship('OrderItem', back_populates='order')
    user = relationship('User', back_populates='orders')

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "total_price": self.total_price,
            "total_quantity": self.total_quantity,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "order_items": [order_item.to_dict() for order_item in self.order_items]
        }
    
def save_order(order: CreateOrder, db: Session = Depends(get_db)):
    db_order = Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

