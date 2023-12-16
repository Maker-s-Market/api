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
from tests.test_sql_app import TestingSessionLocal
from dotenv import load_dotenv

load_dotenv()
COGNITO_USER_CLIENT_ID = os.getenv("COGNITO_USER_CLIENT_ID")

client = TestClient(app)


def get_client_id():
    return COGNITO_USER_CLIENT_ID


ORDER = "/order"

SEND_EMAIL = "routers.orders.send_email"


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

    db.commit()
    db.close()


def login_user1():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()

    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]
    return token


@patch(SEND_EMAIL)
def test_process_payment(mock_send_email):
    mock_send_email.return_value = True
    token = login_user1()
    response = client.post("/api/payment/process-payment?amount=10.0", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["client_secret"] is not None


@patch(SEND_EMAIL)
def test_process_payment_invalid_amount(mock_send_email):
    mock_send_email.return_value = True
    token = login_user1()
    response = client.post("/api/payment/process-payment?amount=0.1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Amount must be greater than 50 cents."


def test_process_payment_not_logged():
    response = client.post("/api/payment/process-payment?amount=10.0")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"
