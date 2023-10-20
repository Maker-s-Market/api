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

global id

class TestProduct:
    @pytest.fixture(autouse=True, scope="session")
    def setup(self):
        log.info("[fixture] starting db container")

        my_sql = MySqlContainer(MYSQL_IMAGE)
        my_sql.start()

        log.info("[fixture] connecting to: {}".format(my_sql.get_connection_url()))

        # generate db url
        os.environ["MYSQL_URL"] = my_sql.get_connection_url()

        yield my_sql

        del os.environ['MYSQL_URL']

    def test_put_product(self):
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

        assert response.status_code == 201, response.text
        
        data = response.json()

        assert data["name"] == "product1"
        assert data["description"] == "product1's description"
        assert data["price"] == 12.5
        assert data["stockable"] == True
        assert data["stock"] == 2
        assert data["categories"] == []

    def test_get_product(self):

        client = TestClient(app)

        response = client.post("/product",
            json = {
                "name": "product2",
                "description": "product2's description",
                "price": 12.5,
                "stockable": True,
                "stock": 2,
                "categories": []
            }
        )

        data = response.json()
        product_id = data["id"]

        response = client.get("/product/" + str(product_id))        #ig this could go wrong

        assert response.status_code == 200
        
        data = response.json()

        assert data["id"] == str(product_id)
        assert data["name"] == "product2"
        assert data["description"] == "product2's description"
        assert data["price"] == 12.5
        assert data["stockable"] == True
        assert data["stock"] == 2
        assert data["categories"] == []

    def test_wrong_category(self):
        client = TestClient(app)

        response = client.post("/product",
            json = {
                "name": "product2",
                "description": "product2's description",
                "price": 12.5,
                "stockable": True,
                "stock": 2,
                "categories": [{
                    "id": "non existent id"
                }]
            }
        )

        assert response.status_code == 404



