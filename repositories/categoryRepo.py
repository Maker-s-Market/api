from sqlalchemy.orm import Session

from schemas.category import CreateCategory
from models.category import create_category, Category as CategoryModel, increment_number_views


def new_category(db: Session, cat: CreateCategory):
    return create_category(db=db, category=cat)


def get_all_categories(db: Session):
    return db.query(CategoryModel).all()


def get_category_by_id(db: Session, category_id: int):
    return db.query(CategoryModel).filter(CategoryModel.id == category_id).first()


def get_products_by_category(db: Session, category_id: int):
    increment_number_views(db=db, category_id=category_id)
    return db.query(CategoryModel).filter(CategoryModel.id == category_id).first().products


def get_top_categories(db: Session):
    return db.query(CategoryModel).order_by(CategoryModel.number_views.desc()).limit(4).all()
