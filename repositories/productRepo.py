from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from auth.auth import get_current_user
from repositories.userRepo import get_user
from models.user import User as UserModel
from db.database import get_db
from schemas.product import CreateProduct
from models.product import create_product, Product as ProductModel


def get_product_by_id(product_id: str, db: Session = Depends(get_db)):
    return db.query(ProductModel).filter(ProductModel.id == product_id).first()


def new_product(product: CreateProduct, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    # cant create more than 5 products if the user
    user = get_user(username, db)
    products = db.query(ProductModel).filter(ProductModel.user_id == user.id).all()
    if len(products) >= 5 and user.role == "Client":
        raise HTTPException(status_code=403,
                            detail="Number of products exceeded, please upgrade to premium or delete existing products.")
    return create_product(db=db, product=product, username=username)


def get_top_products_db(limit: int = 4, db: Session = Depends(get_db)):
    return db.query(ProductModel).order_by(ProductModel.number_views.desc()).limit(limit).all()


def get_products_by_filters(q: str = "",
                            limit: int = 10,
                            price_min: int = 0,
                            price_max: int = 100000000,
                            sort: str = "newest",
                            discount: bool = False,
                            location: str = "",
                            category_id: str = "",
                            db: Session = Depends(get_db)) -> object:
    if sort not in ["newest", "oldest", "price_asc", "price_desc", "relevance"]:
        raise HTTPException(status_code=400, detail="Invalid sort parameter")

    result = (db.query(ProductModel).filter(ProductModel.name.contains(q))
              .filter(ProductModel.price >= price_min)
              .filter(ProductModel.price <= price_max))
    if discount:
        result = result.filter(ProductModel.discount > 0)

    if category_id != "" and category_id is not None:
        result = result.filter(ProductModel.categories.any(id=category_id))

    if location != "" and location is not None:
        result = result.join(UserModel, UserModel.id == ProductModel.user_id)

        result = result.filter(
            (UserModel.city.contains(location)) | (UserModel.region.contains(location))
        )

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


def get_products_by_user_id(user_id: str, db: Session = Depends(get_db)):
    return db.query(ProductModel).filter(ProductModel.user_id == user_id).all()
