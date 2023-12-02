from uuid import uuid4
from uuid import uuid4

from fastapi import Depends
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session

from db.database import Base, get_db
from models.product import Product
from schemas.orderItem import CreateOrderItem, CreateOrderItemOrderId


def random_uuid():
    return str(uuid4())


class OrderItem(Base):
    __tablename__ = "order_item"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    quantity = Column(Integer, index=True, default=0, nullable=False)
    order_id = Column(String(50), ForeignKey("order.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String(50), ForeignKey("product.id", ondelete="CASCADE"), nullable=False)

    def to_dict(self, db: Session = Depends(get_db)):
        return {
            "product": db.query(Product).filter(Product.id == self.product_id).first().to_dict(),
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
