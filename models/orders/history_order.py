import datetime
from uuid import uuid4

from fastapi import Depends
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Session

from db.database import Base, get_db
from models.orders.status import Status


def random_uuid():
    return str(uuid4())


class HistoryOrder(Base):
    __tablename__ = "history_order"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    status = Column(Enum(Status), index=True, default="Accepted", nullable=False)
    data = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                  nullable=False)
    order_id = Column(String(50), ForeignKey("order.id", ondelete="CASCADE"), nullable=False)

    def to_dict(self, db: Session = Depends(get_db)):
        return {
            "status": self.status,
            "data": self.data
        }


def create_history_order(status: str, order_id: str, db: Session = Depends(get_db)):
    db_order = HistoryOrder(status=status, order_id=order_id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order
