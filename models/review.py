import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime

from db.database import Base


class Review(Base):
    __tablename__ = "review"

    # CHANGE TO UUID
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(1000), index=True, nullable=False, default="")

    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now().timestamp(), nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now().timestamp(), nullable=False)

    # # POR CAUSA DO RGPD
    # deleted_at = Column(DateTime(timezone=True), index=True, nullable=True)
    # is_active = Column(Integer, index=True, default=1, nullable=False)

    # BETTER
    user_id = Column(Integer, ForeignKey("user.id"))
    product_id = Column(Integer, ForeignKey("product.id"))
