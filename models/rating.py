import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base


class Rating(Base):
    __tablename__ = "rating"

    # TODO CHANGE TO uuid
    id = Column(Integer, primary_key=True, autoincrement=True)
    rating = Column(Float, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(), nullable=False)

    # # POR CAUSA DO RGPD
    # deleted_at = Column(DateTime(timezone=True), index=True, nullable=True)
    # is_active = Column(Integer, index=True, default=1, nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"))
    product_id = Column(Integer, ForeignKey("product.id"))
