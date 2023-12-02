import os
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

    db.commit()
    db.close()


def test_create_order_success():

    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    order_items = [
        {"product_id": "06e0da01-57fd-2228-95be-0d25c764ea55", "quantity": 2},
        {"product_id": "06e0da01-57fd-2228-95be-0d25c764ea54", "quantity": 1},
    ]

    response = client.post(
        ORDER,
        headers={"Authorization": f"Bearer {token}"},
        json=order_items
    )

    data = response.json()

    assert response.status_code == 201, response.text

    assert "id" in data
    assert data["total_price"] > 0
    assert data["total_quantity"] == 3
    assert len(data["order_items"]) == 2

def test_create_order_no_product_found():

    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    order_items = [
        {"product_id": "06e0da01-57fd-2228-95be-0d25c764ea60", "quantity": 2},
        {"product_id": "06e0da01-57fd-2228-95be-0d25c764ea54", "quantity": 1},
    ]

    response = client.post(
        ORDER,
        headers={"Authorization": f"Bearer {token}"},
        json=order_items
    )

    data = response.json()

    assert response.status_code == 404, response.text
    assert data["detail"] ==  "Product with id: 06e0da01-57fd-2228-95be-0d25c764ea60 was not found."

def test_create_order_product_owner():

    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    order_items = [
        {"product_id": "06e0da01-57fd-2227-95be-0d25c764ea56", "quantity": 2},
        {"product_id": "06e0da01-57fd-2228-95be-0d25c764ea54", "quantity": 1},
    ]

    response = client.post(
        ORDER,
        headers={"Authorization": f"Bearer {token}"},
        json=order_items
    )

    data = response.json()

    assert response.status_code == 400, response.text
    assert data["detail"] ==  "You can't buy your own product."

def test_get_order():

    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    #TODO: mudar isto
    response = client.get(
        ORDER + "?status=Pending&sort=desc_date",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 200, response.text

    response = client.get(
        ORDER + "?status=Pending&sort=asc_date",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 200, response.text
    
    response = client.get(
        ORDER + "?status=Pending&sort=desc_price",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 200, response.text

    response = client.get(
        ORDER + "?status=Pending&sort=asc_price",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 200, response.text

    response = client.get(
        ORDER + "?status=Pending&sort=desc_quantity",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 200, response.text

    response = client.get(
        ORDER + "?status=Pending&sort=asc_quantity",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 200, response.text

def test_get_order_invalid_sort():

    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    #TODO: mudar isto
    response = client.get(
        ORDER + "?status=Pending&sort=invalid_sort",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 400, response.text
    assert data["detail"] == "Sort invalid_sort is not valid."

def test_get_order_invalid_status():

    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    #TODO: mudar isto
    response = client.get(
        ORDER + "?status=InvalidStatus&sort=desc_price",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 400, response.text
    assert data["detail"] == "Status InvalidStatus is not valid."

def test_get_order_seller():

    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "mariana",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.get(
        ORDER + "/seller",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 200, response.text

def test_get_order_by_id_success():

    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    order_items = [
        {"product_id": "06e0da01-57fd-2228-95be-0d25c764ea55", "quantity": 2},
        {"product_id": "06e0da01-57fd-2228-95be-0d25c764ea54", "quantity": 1},
    ]

    response = client.post(
        ORDER,
        headers={"Authorization": f"Bearer {token}"},
        json=order_items
    )

    data = response.json()
    assert response.status_code == 201, response.text
    id = data["id"]

    response = client.get(
        ORDER + "/" + id,
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 200, response.text

def test_order_by_id_order_not_found():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.get(
        ORDER + "/someorderid",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 404, response.text
    assert data["detail"] == "Order with id: someorderid was not found."

def test_order_by_id_order_no_permission():
    
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    order_items = [
        {"product_id": "06e0da01-57fd-2228-95be-0d25c764ea55", "quantity": 2},
        {"product_id": "06e0da01-57fd-2228-95be-0d25c764ea54", "quantity": 1},
    ]

    response = client.post(
        ORDER,
        headers={"Authorization": f"Bearer {token}"},
        json=order_items
    )

    data = response.json()
    assert response.status_code == 201, response.text
    id = data["id"] 

    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "mariana",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.get(
        ORDER + "/" + id,
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 403, response.text
    assert data["detail"] == "You don't have permission to access this order."
