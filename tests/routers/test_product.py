import os

from fastapi.testclient import TestClient
import pytest, logging
from testcontainers.mysql import MySqlContainer
from main import app
from repositories.productRepo import new_product

log = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
MYSQL_IMAGE = "mysql:5.7"
MYSQL_USER = "makers"
MYSQL_PASSWORD = "makers"
MYSQL_DATABASE = "makers"
MYSQL_PORT = 3306

class TestProduct:
    @pytest.fixture(autouse=True, scope="session")
    def setup(self):
        log.info("[fixture] starting db container")

        my_sql = MySqlContainer(MYSQL_IMAGE)
        my_sql.start()

        log.info("[fixture] connecting to: {}".format(my_sql.get_connection_url()))

        # generate db url
        os.environ["MYSQL_URL"] = my_sql.get_connection_url()

        yield

        del os.environ['MYSQL_URL']

    def test_put_produtct(self):
        client = TestClient(app)
        
        response = client.post("/product",
            json = {
                "name": "product1",
                "description": "product1's description",
                "price": 12.5,
                "stockable": True,
                "stock": 2,
                "categories": []
            }
        )

        assert response.status_code == 201

    def test_put_existing_product(self):
        client = TestClient(app)
        
        response = client.post("/product",
            json = {
                "name": "product1",
                "description": "product1's description",
                "price": 12.5,
                "stockable": True,
                "stock": 2,
                "categories": []
            }
        )

        response = client.post("/product",
            json = {
                "name": "product1",
                "description": "product1's description",
                "price": 12.5,
                "stockable": True,
                "stock": 2,
                "categories": []
            }
        )

        assert response.status_code == 400


