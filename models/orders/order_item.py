import datetime
from uuid import uuid4

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from db.database import Base


def random_uuid():
    return str(uuid4())


# status : placed, cancelled, accepted, rejected, send

class OrderItem(Base):
    __tablename__ = "order_item"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    order_id = Column(String(50), ForeignKey('order.id'))
    product_id = Column(String(50), ForeignKey('product.id'))
    quantity = Column(Integer, index=True, default=0, nullable=False)
    order = relationship('Order', back_populates='order_items')
    product = relationship('Product', back_populates='order_items')

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
        }
