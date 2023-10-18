import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from db.base import Base
from models.product import Product
from models.category import Category
from models.rating import Rating
from models.review import Review
from models.user import User
from models.wishList import Wishlist


def get_db():
    SQLALCHEMY_DATABASE_URL = os.environ.get("MYSQL_URL", "mysql+pymysql://makers:makers@localhost/makers")

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


    User.metadata.create_all(bind=engine)
    Product.metadata.create_all(bind=engine)
    Category.metadata.create_all(bind=engine)
    Rating.metadata.create_all(bind=engine)
    Review.metadata.create_all(bind=engine)
    Wishlist.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
