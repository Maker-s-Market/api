import datetime
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Float, ForeignKey

from db.database import Base


class Rating(Base):
    __tablename__ = "rating"

    id = Column(String(50), primary_key=True, index=True, default=str(uuid4()))
    rating = Column(Float, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(), nullable=False)

    user_id = Column(String(50), ForeignKey("user.id"))
    product_id = Column(String(50), ForeignKey("product.id"))
