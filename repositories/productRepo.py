from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.product import CreateProduct
from models.product import create_product, Product as ProductModel


def get_product_by_id(product_id: str, db: Session = Depends(get_db)):
    return db.query(ProductModel).filter(ProductModel.id == product_id).first()


def new_product(product: CreateProduct, db: Session = Depends(get_db)):
    return create_product(db=db, product=product)


def get_top_products_db(db: Session = Depends(get_db)):
    return db.query(ProductModel).order_by(ProductModel.number_views.desc()).limit(4).all()


def get_all_products(db: Session = Depends(get_db)):
    return db.query(ProductModel).filter().all()


# get products by this filters
# query
def get_products_by_filters(q: str = "", price_min: int = None, price_max: int = None,
                            limit: int = 10,
                            db: Session = Depends(get_db)):
    return (db.query(ProductModel)
            .filter(ProductModel.name.contains(q))
            .filter(ProductModel.price >= price_min)
            .filter(ProductModel.price <= price_max)
            .order_by(ProductModel.created_at.desc())
            .limit(limit)
            .all())
