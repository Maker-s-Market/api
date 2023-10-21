from fastapi import Depends, HTTPException
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


def get_products_by_filters(q: str = "",
                            limit: int = 10,
                            price_min: int = 0,
                            price_max: int = 100000000,
                            sort: str = "newest",
                            discount: bool = False,
                            category_id: str = None,
                            db: Session = Depends(get_db)) -> object:
    if sort not in ["newest", "oldest", "price_asc", "price_desc", "relevance"]:
        raise HTTPException(status_code=400, detail="Invalid sort parameter")

    result = (db.query(ProductModel).filter(ProductModel.name.contains(q))
                .filter(ProductModel.price >= price_min)
                .filter(ProductModel.price <= price_max))
    if discount:
        result = result.filter(ProductModel.discount > 0)

    if category_id is not None:
        result = result.filter(ProductModel.categories.any(id=category_id))

    if sort == "newest":
        return result.order_by(ProductModel.created_at.desc()).limit(limit).all()
    elif sort == "oldest":
        return result.order_by(ProductModel.created_at.asc()).limit(limit).all()
    elif sort == "price_asc":
        return result.order_by(ProductModel.price.asc()).limit(limit).all()
    elif sort == "price_desc":
        return result.order_by(ProductModel.price.desc()).limit(limit).all()
    elif sort == "relevance":
        return result.order_by(ProductModel.number_views.desc()).limit(limit).all()
    else:
        return result.limit(limit).all()


