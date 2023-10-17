import uuid
import datetime
import enum
from uuid import UUID

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum, DateTime, func, Float
from sqlalchemy.orm import relationship

from db.database import Base


class Role(enum.Enum):
    Admin = "Admin"
    Client = "Client"
    Premium = "Premium"


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), index=True, nullable=False)
    hashed_password = Column(String(200), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now().timestamp(), nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True)
    is_active = Column(Boolean, index=True, default=True)
    role = Column(Enum(Role))  # Ver se isto dá certo ou não

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), index=True, unique=True, nullable=False)
    slug = Column(String(200), index=True, unique=True, nullable=False)
    description = Column(String(200), index=True, nullable=False)
    created_at = Column(String(200), index=True, default=datetime.datetime.now().timestamp(), nullable=False)
    updated_at = Column(String(200), index=True)

    products = relationship("Product", back_populates="category")



class Review(Base):
    __tablename__ = "review"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(String(255), index=True, default=datetime.datetime.now().timestamp(), nullable=False)
    updated_at = Column(String(255), index=True)
    comment = Column(String(1000), index=True, nullable=False, default="")

    user_id = Column(Integer, ForeignKey("user.id"))
    product_id = Column(Integer, ForeignKey("product.id"))

class Rating(Base):
    __tablename__ = "rating"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(String(255), index=True, default=datetime.datetime.now().timestamp(), nullable=False)
    updated_at = Column(String(255), index=True)
    rating = Column(Float, index=True, nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"))
    product_id = Column(Integer, ForeignKey("product.id"))

class WishList(Base):
    __tablename__ = "wishlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(String(255), index=True, default=datetime.datetime.now().timestamp(), nullable=False)
    updated_at = Column(String(255), index=True)

    user_id = Column(Integer, ForeignKey("user.id"))
    product_id = Column(Integer, ForeignKey("product.id"))

class ShoppingCart(Base):
    __tablename__ = "shoppingcart"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(String(255), index=True, default=datetime.datetime.now().timestamp(), nullable=False)
    updated_at = Column(String(255), index=True)

    user_id = Column(Integer, ForeignKey("user.id"))

class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    created_at = Column(String(255), index=True, default=datetime.datetime.now().timestamp(), nullable=False)
    updated_at = Column(String(255), index=True)
    status = Column(Integer, index=True, default=0, nullable=False)
    
    cart_id = Column(Integer, ForeignKey("shoppingcart.id"))

class OrderLine(Base):
    __tablename__ = "orderline"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(String(255), index=True, default=datetime.datetime.now().timestamp(), nullable=False)
    updated_at = Column(String(255), index=True)
    amount = Column(Float, index=True, nullable=False)
    line_price = Column(Float, index=True, nullable=False)
    status = Column(Integer, index=True, default=0, nullable=False)

    product_id = Column(Integer, ForeignKey("product.id"))
    order_id = Column(Integer, ForeignKey("order.id"))