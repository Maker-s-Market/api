import datetime
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship

from db.database import Base

ProductWishlist = Table(
    'product_wishlist',
    Base.metadata,
    Column('product_id', String(50), ForeignKey('product.id')),
    Column('wishlist_id', String(50), ForeignKey('wishlist.id'))
)


def random_uuid():
    return str(uuid4())


class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)
    products = relationship("Product", secondary=ProductWishlist, back_populates="wishlists")
