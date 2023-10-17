from sqlalchemy.orm import Session

from schemas.category import CreateCategory, CategoryBase
from models.product import Product as ProductModel

def get_product_by_id(product_id: int, db: Session):
    return db.query(ProductModel).filter(ProductModel.id == product_id).first()