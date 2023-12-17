import unittest

from db.insert_data import insert_data
from models.category import Category as CategoryModel
from models.orders.order import Order
from models.product import Product
from models.ratingProduct import RatingProduct
from models.ratingUser import RatingUser
from models.user import User

from tests.test_sql_app import TestingSessionLocal


class TestInsertData(unittest.TestCase):
    def test_valid_insert_data(self):
        db = TestingSessionLocal()
        insert_data(db)
        categories = db.query(CategoryModel).all()
        user = db.query(User).all()
        products = db.query(Product).all()
        ratings_products = db.query(RatingProduct).all()
        ratings_users = db.query(RatingUser).all()
        orders = db.query(Order).all()

        assert len(products) == 39
        assert len(ratings_products) == 14
        assert len(ratings_users) == 7
        assert len(categories) == 12
        assert len(user) == 4
        assert len(orders) == 2
