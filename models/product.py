import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, Session

from db.base import Base
from models.category import Category, ProductCategory
from models.wishList import ProductWishlist
from schemas.product import CreateProduct
from fastapi import HTTPException
from sqlalchemy.ext.declarative import declarative_base


class Product(Base):
    __tablename__ = "product"

    #  TODO CHANGE TO uuid
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
    wishlists = relationship("Wishlist", secondary=ProductWishlist, back_populates="products")

    def increment_number_views(self, db: Session):
        self.number_views += 1
        self.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(self)

    def add_category(self, category: Category):
        self.categories.append(category)

    def remove_category(self, category: Category):
        self.categories.remove(category)

    def add_categories(self, categories: list[Category]):
        self.categories.extend(categories)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stockable': self.stockable,
            'stock': self.stock,
            'discount': self.discount,
            'number_views': self.number_views,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


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
        db_product.add_categories(categories)
        db.commit()
        db.refresh(db_product)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error creating product")
    return db_product


def edit_product():
    pass


def delete_product(product_id: int, db: Session):
    prod = None

    pass

