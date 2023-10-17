import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base


# class Rating(Base):
#     __tablename__ = "rating"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     created_at = Column(String(255), index=True, default=datetime.datetime.now().timestamp(), nullable=False)
#     updated_at = Column(String(255), index=True)
#     rating = Column(Float, index=True, nullable=False)
#
#     user_id = Column(Integer, ForeignKey("user.id"))
#     product_id = Column(Integer, ForeignKey("product.id"))
