import unittest

from db.insert_data import insert_data
from models.category import Category as CategoryModel

from tests.test_sql_app import TestingSessionLocal

class TestInsertData(unittest.TestCase):
    def test_valid_insert_data(self):
        db = TestingSessionLocal()
        insert_data(db)
        categories = db.query(CategoryModel).all()

        assert len(categories) == 12
