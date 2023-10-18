import datetime
import uuid
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import Session, relationship

from sqlalchemy.ext.declarative import declarative_base

from db.base import Base
from schemas.category import CreateCategory

ProductCategory = Table(
    'product_category',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('product.id')),
    Column('category_id', Integer, ForeignKey('category.id'))
)


class Category(Base):
    __tablename__ = "category"

    # TODO CHANGE TO uuid
    id = Column(Integer, primary_key=True, autoincrement=True)
    # id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), index=True, unique=True, nullable=False)
    slug = Column(String(200), index=True, unique=True, default="", nullable=False)
    icon = Column(String(200), index=True, nullable=False)
    number_views = Column(Integer, index=True, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)

    # POR CAUSA DO RGPD
    deleted_at = Column(DateTime(timezone=True), index=True, nullable=True)
    is_active = Column(Integer, index=True, default=1, nullable=False)

    products = relationship('Product', secondary=ProductCategory, back_populates='categories')

    def increment_number_views(self, db: Session):
        self.number_views += 1
        self.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(self)

    def update_category(self, db: Session, category: CreateCategory):
        self.name = category.name
        self.slug = category.slug
        self.icon = category.icon
        self.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(self)
        return self

    def delete_category(self, db: Session):
        self.deleted_at = datetime.datetime.now()
        self.is_active = 0
        db.commit()
        db.refresh(self)
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "icon": self.icon,
            "number_views": self.number_views,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


def create_category(db: Session, category: CreateCategory):
    if db.query(Category).filter(Category.name == category.name).first():
        raise HTTPException(status_code=400, detail="Category already exists")
    db_category = Category(**category.dict())
    db_category.slug = db_category.name.replace(" ", "-").lower()
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category
