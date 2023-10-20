from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.product import CreateProduct
from models.product import create_product, Product as ProductModel


def get_product_by_id(product_id: str, db: Session = Depends(get_db)):
    return db.query(ProductModel).filter(ProductModel.id == product_id).first()


def new_product(product: CreateProduct, db: Session = Depends(get_db)):
    return create_product(db=db, product=product)
