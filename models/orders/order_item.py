import datetime
from uuid import uuid4
from fastapi import Depends

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, Session

from db.database import Base, get_db
from schemas.orderItem import CreateOrderItem, CreateOrderItemOrderId

OrderAndOrderItem = Table(
    'order_and_order_item',
    Base.metadata,
    Column('order_id', String(50), ForeignKey('order.id')),
    Column('order_item_id', String(50), ForeignKey('order_item.id'))
)


def random_uuid():
    return str(uuid4())


class OrderItem(Base):
    __tablename__ = "order_item"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    quantity = Column(Integer, index=True, default=0, nullable=False)
    order = relationship("Order", secondary=OrderAndOrderItem, back_populates="order_items")
    product_id = Column(String(50), ForeignKey("product.id", ondelete="CASCADE"), nullable=False)

    def to_dict(self):
        return {
            "product": self.product.to_dict(),
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
