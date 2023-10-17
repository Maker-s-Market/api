import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Table
from sqlalchemy.orm import relationship

from db.database import Base

ProductWishlist = Table(
    'product_wishlist',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('product.id')),
    Column('wishlist_id', Integer, ForeignKey('wishlist.id'))
)


class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)
    products = relationship("Product", secondary=ProductWishlist, back_populates="wishlists")
