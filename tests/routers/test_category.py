import os

from fastapi.testclient import TestClient
import pytest, logging
from testcontainers.mysql import MySqlContainer
from main import app

log = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
MYSQL_IMAGE = "mysql:5.7"
MYSQL_USER = "makers"
MYSQL_PASSWORD = "makers"
MYSQL_DATABASE = "makers"
MYSQL_PORT = 3306


class TestMain:
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

    def test_read_main(self):
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "hello World!"}
