from sqlalchemy.orm import Session

from schemas.product import CreateProduct
from models.product import create_product, Product as ProductModel


def get_product_by_id(product_id: int, db: Session):
    return db.query(ProductModel).filter(ProductModel.id == product_id).first()


def new_product(db: Session, product: CreateProduct):
    return create_product(db=db, product=product)
