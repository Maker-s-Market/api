import datetime

from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import Session, relationship

from db.database import Base
from schemas.category import CreateCategory

ProductCategory = Table(
    'product_category',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('product.id')),
    Column('category_id', Integer, ForeignKey('category.id'))
)


class Category(Base):
    __tablename__ = "category"

    # CHANGE TO uuid
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), index=True, unique=True, nullable=False)
    slug = Column(String(200), index=True, unique=True, nullable=False)
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


def create_category(db: Session, category: CreateCategory):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def increment_number_views(db: Session, category_id: int):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    db_category.number_views += 1
    db.commit()
    db.refresh(db_category)
    return db_category
