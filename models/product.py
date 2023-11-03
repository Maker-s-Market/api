import datetime
from uuid import uuid4

from fastapi import HTTPException, Depends
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Session
from auth.auth import get_current_user

from db.database import get_db, Base
from models.category import Category, ProductCategory
from models.wishList import ProductWishlist
from repositories.userRepo import get_user
from schemas.product import CreateProduct


def random_uuid():
    return str(uuid4())


class Product(Base):
    __tablename__ = "product"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    name = Column(String(255), index=True, nullable=False)
    description = Column(String(800), index=True, nullable=False)
    price = Column(Float, index=True, nullable=False)
    stockable = Column(Boolean, index=True, nullable=False)
    stock = Column(Integer, index=True)
    discount = Column(Integer, index=True, default=0)
    number_views = Column(Integer, index=True, default=0)
    image = Column(String(255), index=True, nullable=True)

    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)

    user_id = Column(String(50), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)  # TODO CHANGE TO FALSE
    categories = relationship('Category', secondary=ProductCategory, back_populates='products')
    wishlists = relationship("Wishlist", secondary=ProductWishlist, back_populates="products")

    def increment_number_views(self, db: Session = Depends(get_db)):
        self.number_views += 1
        self.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(self)

    def add_categories(self, categories, db: Session = Depends(get_db)):
        self.categories.extend(categories)
        db.commit()
        db.refresh(self)

    def update_product(self, db: Session, product: CreateProduct):
        self.name = product.name
        self.description = product.description
        self.price = product.price
        self.stockable = product.stockable
        self.stock = product.stock
        self.discount = product.discount
        self.categories = []
        for category in product.categories:
            db_category = db.query(Category).filter(Category.id == category.id).first()
            if db_category:
                self.categories.append(db_category)
            else:
                raise HTTPException(status_code=404, detail="Category not found")
        self.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session = Depends(get_db)):
        db.delete(self)
        db.commit()
        return self

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stockable': self.stockable,
            'stock': self.stock,
            'discount': self.discount,
            'image': self.image,
            'number_views': self.number_views,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'categories': [category.to_dict() for category in self.categories]
        }


def create_product(product: CreateProduct, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    categories = set()
    for category in product.categories:
        db_category = db.query(Category).filter(Category.id == category.id).first()
        if db_category:
            categories.add(db_category)
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    product.categories = []
    try:
        user = get_user(username, db)
        db_product = Product(**product.model_dump())
        db_product.user_id = user.id
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        db_product.add_categories(categories=categories, db=db)
    except Exception:
        raise HTTPException(status_code=400, detail="Error creating product")
    return db_product
