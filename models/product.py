
import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

from db.database import Base, engine

ProductCategory = Table(
    'product_category',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('product.id')),
    Column('category_id', Integer, ForeignKey('category.id'))
)


class Product(Base):
    __tablename__ = "product"

    # CHANGE TO uuid
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, unique=True)
    description = Column(String(255), index=True, nullable=False)
    price = Column(Float, index=True, nullable=False)
    stockable = Column(Boolean, index=True, nullable=False)
    stock = Column(Integer, index=True)
    discount = Column(Float, index=True, default=0)
    numberViews = Column(Integer, index=True, default=0)

    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now().timestamp(), nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now().timestamp(), nullable=False)

    # POR CAUSA DO RGPD
    deleted_at = Column(DateTime(timezone=True), index=True, nullable=True)
    is_active = Column(Integer, index=True, default=1, nullable=False)

    # Change to image
    # image = Column()

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    categories = relationship('Category', secondary=ProductCategory, back_populates='products')
