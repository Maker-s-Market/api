import datetime
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, String, DateTime

from db.database import Base
from utils import generate_uuid


def random_uuid():
    return str(uuid4())

class Review(Base):
    __tablename__ = "review"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    text = Column(String(1000), index=True, nullable=False, default="")

    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now().timestamp(), nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now().timestamp(), nullable=False)

    user_id = Column(String(50), ForeignKey("user.id"))
    product_id = Column(String(50), ForeignKey("product.id"))
