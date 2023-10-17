import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, Session

from db.database import Base, engine
from models.category import Category, ProductCategory
from schemas.product import CreateProduct
from fastapi import HTTPException


class Product(Base):
    __tablename__ = "product"

    # CHANGE TO uuid
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(String(255), index=True, nullable=False)
    price = Column(Float, index=True, nullable=False)
    stockable = Column(Boolean, index=True, nullable=False)
    stock = Column(Integer, index=True)
    discount = Column(Float, index=True, default=0)
    number_views = Column(Integer, index=True, default=0)

    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)

    # POR CAUSA DO RGPD
    deleted_at = Column(DateTime(timezone=True), index=True, nullable=True)
    is_active = Column(Integer, index=True, default=1, nullable=False)

    # Change to image
    # image = Column()

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=True)
    categories = relationship('Category', secondary=ProductCategory, back_populates='products')


def increment_number_views(db: Session, product_id: int):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    db_product.number_views += 1
    db.commit()
    db.refresh(db_product)
    return db_product


def create_product(db: Session, product: CreateProduct):
    categories = []
    for category in product.categories:
        db_category = db.query(Category).filter(Category.id == category.id).first()
        if db_category:
            categories.append(db_category)
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    product.categories = []
    try:
        db_product = Product(**product.dict())
        db.add(db_product)
        db_product.categories = categories
        db.commit()
        db.refresh(db_product)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error creating product")
    return db_product


def edit_product():
    pass


def delete_product():
    pass


def read_product():
    pass
