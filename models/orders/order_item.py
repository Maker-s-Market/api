import datetime
from uuid import uuid4
from fastapi import Depends

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Session

from db.database import Base, get_db
from schemas.orderItem import CreateOrderItem


def random_uuid():
    return str(uuid4())


# status : placed, cancelled, accepted, rejected, send

class OrderItem(Base):
    __tablename__ = "order_item"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    order_id = Column(String(50), ForeignKey('order.id'))
    product_id = Column(String(50), ForeignKey('product.id'))
    quantity = Column(Integer, index=True, default=0, nullable=False)
    status = Column(String, index=True, default="placed", nullable=False)
    order = relationship('Order', back_populates='order_items')
    product = relationship('Product', back_populates='order_items')

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
        }
    
def save_order_item(item: CreateOrderItem, order_id: str, db: Session = Depends(get_db)):
    order_item = OrderItem(
        order_id=order_id,
        product_id=item.product_id,
        quantity=item.quantity,
        status="placed",
    )
    db.add(order_item)
    db.commit()
    db.refresh(order_item)
    
    return order_item