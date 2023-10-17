from sqlalchemy.orm import Session

from schemas.product import CreateProduct
from models.product import create_product, Product as ProductModel


def new_product(db: Session, product: CreateProduct):
    return create_product(db=db, product=product)

