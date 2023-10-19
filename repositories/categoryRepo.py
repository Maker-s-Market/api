from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from models.category import create_category, Category as CategoryModel
from schemas.category import CreateCategory


def new_category(cat: CreateCategory, db: Session = Depends(get_db)):
    return create_category(db=db, category=cat)


def get_all_categories(db: Session = Depends(get_db)):
    return db.query(CategoryModel).all()


def get_category_by_id(category_id: int, db: Session = Depends(get_db)):
    return db.query(CategoryModel).filter(CategoryModel.id == category_id).first()


def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    return db.query(CategoryModel).filter(CategoryModel.id == category_id).first().products


def get_top_categories(db: Session = Depends(get_db)):
    return db.query(CategoryModel).order_by(CategoryModel.number_views.desc()).limit(4).all()
