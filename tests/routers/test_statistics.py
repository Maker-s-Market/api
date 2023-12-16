import os
from unittest.mock import patch
from uuid import uuid4

import pytest
import math

from fastapi.testclient import TestClient

from main import app
from models.category import Category
from models.product import Product
from models.user import User
from models.orders.order import Order
from tests.routers.test_order_IT import INVOKE_USER_INFO
from tests.test_sql_app import TestingSessionLocal
from dotenv import load_dotenv

load_dotenv()
COGNITO_USER_CLIENT_ID = os.getenv("COGNITO_USER_CLIENT_ID")

client = TestClient(app)

SELLER_STATISTICS = "/api/statistics/seller"
BUYER_STATISTICS = "/api/statistics/buyer"


def get_client_id():
    return COGNITO_USER_CLIENT_ID


@pytest.fixture(scope="module", autouse=True)
def load_data():
    db = TestingSessionLocal()
    db.query(Category).delete()
    db.query(Product).delete()
    db.query(User).delete()
    user1 = User(id=str(uuid4()), name="Bruna", username="brums21", email="brums21.10@gmail.com", city="pombal",
                 region="nao existe", photo="", role="Premium")
    user2 = User(id=str(uuid4()), name="Mariana", username="mariana", email="marianaandrade@ua.pt", city="aveiro",
                 region="nao sei", photo="", role="Premium")
    db.add(user1)
    db.add(user2)
    db.add(Category(id="06e0da01-57fd-4441-95be-0d25c764ea57", name="Category1x", icon="icon1", slug="category1x"))
    db.add(Product(id="06e0da01-57fd-2227-95be-0d25c764ea56", name="random product 1", description="some description 1",
                   price=12.0, stockable=False, user_id=user1.id))
    db.add(Product(id="06e0da01-57fd-2228-95be-0d25c764ea55", name="random product 2", description="some description 2",
                   price=11.0, stockable=True, user_id=user2.id))
    db.add(Product(id="06e0da01-57fd-2228-95be-0d25c764ea54", name="random product 3", description="some description 3",
                   price=11.0, stockable=True, user_id=user2.id))
    db.add(Product(id="06e0da01-57fd-2229-95be-123455555566", name="random product 4", description="some description 4",
                   price=10.0, stockable=True, user_id="123456789023456789"))

    category = Category(id="06e0da01-57fd-2229-95be-123455555567", name="category name", slug="slug", icon="some icon")
    db.add(category)

    db.add(Product(id="06e0da01-57fd-2228-95be-0d25c764ea58", name="random product 2", description="some description 2",
                   price=11.0, stockable=True, user_id=user2.id, categories=[category]))

    db.commit()
    db.close()


def login_user_1():
    os.environ['COGNITO_USER_CLIENT_ID'] = os.getenv("COGNITO_USER_CLIENT_ID")
    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]
    return token


def login_user_2():
    os.environ['COGNITO_USER_CLIENT_ID'] = os.getenv("COGNITO_USER_CLIENT_ID")
    response = client.post("/api/auth/sign-in", json={
        "identifier": "mariana",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]
    return token


def test_get_statistics_seller():
    response = client.get(
        SELLER_STATISTICS,
        headers={"Authorization": f"Bearer {login_user_1()}"},
    )

    assert response.status_code == 200, response.text


def test_get_statistics_buyer_no_orders():
    response = client.get(
        BUYER_STATISTICS,
        headers={"Authorization": f"Bearer {login_user_1()}"},
    )

    data = response.json()
    assert response.status_code == 200, response.text
    assert data["statistics"][0]["name"] == "Max Product"
    assert data["statistics"][0]["value"] == ""
    assert data["statistics"][1]["name"] == "Max Category"
    assert data["statistics"][1]["value"] == ""
    assert data["statistics"][2]["name"] == "Max Productor"
    assert data["statistics"][2]["value"] == ""


@patch(INVOKE_USER_INFO)
def test_get_statistics_buyer_no_category(invoke_function):
    invoke_function.return_value = None
    order_items = [
        {"product_id": "06e0da01-57fd-2228-95be-0d25c764ea55", "quantity": 2},
        {"product_id": "06e0da01-57fd-2228-95be-0d25c764ea54", "quantity": 1},
    ]

    response = client.post(
        "/api/order",
        headers={"Authorization": f"Bearer {login_user_1()}"},
        json=order_items
    )

    assert response.status_code == 201, response.text

    response = client.get(
        BUYER_STATISTICS,
        headers={"Authorization": f"Bearer {login_user_1()}"},
    )

    data = response.json()
    assert response.status_code == 200, response.text
    assert data["statistics"][0]["name"] == "Max Product"
    assert data["statistics"][0]["value"] != ""
    assert data["statistics"][1]["name"] == "Max Category"
    assert data["statistics"][1]["value"] == ""
    assert data["statistics"][2]["name"] == "Max Productor"
    assert data["statistics"][2]["value"] != ""


@patch(INVOKE_USER_INFO)
def test_get_statistics_buyer_accepted(invoke_function):
    invoke_function.return_value = None
    order_items = [
        {"product_id": "06e0da01-57fd-2228-95be-0d25c764ea58", "quantity": 2},
        {"product_id": "06e0da01-57fd-2228-95be-0d25c764ea54", "quantity": 1},
    ]

    response = client.post(
        "/api/order",
        headers={"Authorization": f"Bearer {login_user_1()}"},
        json=order_items
    )

    assert response.status_code == 201, response.text

    response = client.get(
        BUYER_STATISTICS,
        headers={"Authorization": f"Bearer {login_user_1()}"},
    )

    data = response.json()
    assert response.status_code == 200, response.text
    assert data["statistics"][0]["name"] == "Max Product"
    assert data["statistics"][0]["value"] != ""
    assert data["statistics"][1]["name"] == "Max Category"
    assert data["statistics"][1]["value"] != ""
    assert data["statistics"][2]["name"] == "Max Productor"
    assert data["statistics"][2]["value"] != ""
