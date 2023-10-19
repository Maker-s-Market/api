from sqlalchemy.orm import Session

from schemas.product import CreateProduct
from models.product import create_product
from db.database import get_db
from fastapi import Depends

def new_product(product: CreateProduct, db: Session = Depends(get_db)):
    return create_product(db=db, product=product)

