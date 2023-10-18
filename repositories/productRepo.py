from sqlalchemy.orm import Session

from schemas.product import CreateProduct
from models.product import create_product, read_product, Product as ProductModel

def get_product_by_id(product_id: int, db: Session):
    return read_product(product_id, db)

def new_product(db: Session, product: CreateProduct):
    return create_product(db=db, product=product)
