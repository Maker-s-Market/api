from models.category import Category
from models.orders.order import Order
from models.orders.order_item import OrderItem
from models.product import Product
from models.ratingProduct import RatingProduct
from models.ratingUser import RatingUser
from models.review import Review
from models.user import User
from models.wishList import Wishlist

from db.database import engine


def create_tables():
    User.metadata.create_all(bind=engine)
    Product.metadata.create_all(bind=engine)
    Category.metadata.create_all(bind=engine)
    RatingProduct.metadata.create_all(bind=engine)
    RatingUser.metadata.create_all(bind=engine)
    Review.metadata.create_all(bind=engine)
    Wishlist.metadata.create_all(bind=engine)
    Order.metadata.create_all(bind=engine)
    OrderItem.metadata.create_all(bind=engine)
