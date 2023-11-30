import datetime
from uuid import uuid4
from fastapi import Depends

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Session

from db.database import Base, get_db
from schemas.orderItem import CreateOrderItem, CreateOrderItemOrderId


def random_uuid():
    return str(uuid4())


# status : placed, cancelled, accepted, rejected, send

class OrderItem(Base):
    __tablename__ = "order_item"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    order_id = Column(String(50), ForeignKey('order.id'))
    product_id = Column(String(50), ForeignKey('product.id'))
    quantity = Column(Integer, index=True, default=0, nullable=False)
    status = Column(String(50), index=True, default="placed", nullable=False)
    order = relationship('Order', back_populates='order_items')
    product = relationship('Product', back_populates='order_items')

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
        }
    
def save_order_item(item: CreateOrderItem, order_id: str, db: Session = Depends(get_db)):
    order_item = CreateOrderItemOrderId(
        order_id=order_id,
        product_id=item.product_id,
        quantity=item.quantity
    )
    db_order_item = OrderItem(**order_item.model_dump())
    db.add(db_order_item)
    db.commit()
    db.refresh(db_order_item)
    
    return db_order_item