import os
from uuid import uuid4

import pytest
import math

from fastapi.testclient import TestClient

from main import app
from models.category import Category
from models.product import Product
from models.user import User
from schemas.product import CreateProduct, UpdateDiscount
from tests.test_sql_app import TestingSessionLocal
from dotenv import load_dotenv

load_dotenv()  # import pytest.ini env variables

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def load_data():
    db = TestingSessionLocal()
    db.query(Category).delete()
    db.query(User).delete()
    db.query(Product).delete()
    user1 = User(id=str(uuid4()), name="Bruna", username="brums21", email="brums21.10@gmail.com", city="pombal",
                 region="nao existe", photo="", role="Client")
    user2 = User(id=str(uuid4()), name="Mariana", username="mariana", email="marianaandrade@ua.pt", city="aveiro",
                 region="nao sei", photo="", role="Client")
    db.add(user1)
    db.add(user2)
    db.add(Category(id="06e0da01-57fd-4441-95be-0d25c764ea57", name="Category1x", icon="icon1", slug="category1x"))
    db.add(Product(id="06e0da01-57fd-2227-95be-0d25c764ea56", name="random product 1", description="some description 1",
                   price=12.0, stockable=False, user_id=user1.id))
    db.add(Product(id="06e0da01-57fd-2228-95be-0d25c764ea57", name="random product 2", description="some description 2",
                   price=11.0, stockable=True, user_id=user2.id))
    db.add(Product(id="06e0da01-57fd-2229-95be-123455555566", name="random product 3", description="some description 3",
                   price=10.0, stockable=True, user_id="123456789023456789"))

    db.commit()
    db.close()


def login_user1():
    os.environ['COGNITO_USER_CLIENT_ID'] = os.getenv("COGNITO_USER_CLIENT_ID")

    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]
    return token


def login_user2():
    os.environ['COGNITO_USER_CLIENT_ID'] = os.getenv("COGNITO_USER_CLIENT_ID")

    response = client.post("/auth/sign-in", json={
        "identifier": "mariana",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]
    return token


def test_put_products_discount_not_owner():
    upd_discount = UpdateDiscount(product_id="06e0da01-57fd-2227-95be-0d25c764ea56", discount=0.5)

    response = client.put("/products/discount",
                          json=upd_discount.model_dump(),
                          headers={"Authorization": "Bearer " + login_user2()})

    assert response.status_code == 403, response.text
    assert response.json() == {'detail': "Only the user can change their product's discount"}


def test_put_products_discount_not_found():
    upd_discount = UpdateDiscount(product_id="06e0da01-57fd-2227-95be-0d25c764ea59", discount=0.5)

    response = client.put("/products/discount",
                          json=upd_discount.model_dump(),
                          headers={"Authorization": "Bearer " + login_user1()})

    assert response.status_code == 404, response.text
    assert response.json() == {'detail': 'Product not found'}


def test_put_products_discount():
    upd_discount = UpdateDiscount(product_id="06e0da01-57fd-2227-95be-0d25c764ea56", discount=0.5)

    response = client.put("/products/discount",
                          json=upd_discount.model_dump(),
                          headers={"Authorization": "Bearer " + login_user1()})

    assert response.status_code == 200, response.text
    data = response.json()
    assert math.isclose(data["discount"], 0.5, abs_tol=0.001)
    assert data["id"] == "06e0da01-57fd-2227-95be-0d25c764ea56"
    assert data["name"] == "random product 1"








