import os
from uuid import uuid4

import pytest
import math

from fastapi.testclient import TestClient

from main import app
from models.category import Category
from models.product import Product
from models.user import User
from tests.test_sql_app import TestingSessionLocal
from dotenv import load_dotenv

load_dotenv() 
COGNITO_USER_CLIENT_ID = os.getenv("COGNITO_USER_CLIENT_ID")

client = TestClient(app)


def get_client_id():
    return COGNITO_USER_CLIENT_ID

#user1 - username: brums21, role-client
#user2 - username: mariana, role-premium
@pytest.fixture(scope="module", autouse=True)
def load_data():
    db = TestingSessionLocal()
    db.query(Category).delete()
    db.query(Product).delete()
    db.query(User).delete()
    user1 = User(id=str(uuid4()), name="Bruna", username="brums21", email="brums21.10@gmail.com", city="pombal",
                 region="nao existe", photo="", role="Client")
    user2 = User(id=str(uuid4()), name="Mariana", username="mariana", email="marianaandrade@ua.pt", city="aveiro",
                 region="nao sei", photo="", role="Premium")
    db.add(user1)
    db.add(user2)
    db.add(Category(id="06e0da01-57fd-4441-95be-0d25c764ea57", name="Category1x", icon="icon1", slug="category1x"))
    
    db.add(Product(id="06e0da01-57fd-2227-95be-0d25c764ea56", name="random product 1", description="some description 1",
                   price=12.0, stockable=False, user_id=user1.id))
    db.add(Product(id="06e0da01-57fd-2227-95be-0d25c764ea57", name="random product 2", description="some description 2",
                   price=12.0, stockable=False, user_id=user1.id))
    db.add(Product(id="06e0da01-57fd-2227-95be-0d25c764ea58", name="random product 3", description="some description 3",
                   price=12.0, stockable=False, user_id=user1.id))
    db.add(Product(id="06e0da01-57fd-2228-95be-0d25c764ea59", name="random product 4", description="some description 4",
                   price=11.0, stockable=True, user_id=user1.id))
    db.add(Product(id="06e0da01-57fd-2228-95be-0d25c764ea60", name="random product 4", description="some description 4",
                   price=11.0, stockable=True, user_id=user1.id))
    
    db.add(Product(id="06e0da01-57fd-2227-95be-0d25c764ea61", name="random product 1", description="some description 1",
                   price=12.0, stockable=False, user_id=user2.id))
    db.add(Product(id="06e0da01-57fd-2227-95be-0d25c764ea62", name="random product 2", description="some description 2",
                   price=12.0, stockable=False, user_id=user2.id))
    db.add(Product(id="06e0da01-57fd-2227-95be-0d25c764ea63", name="random product 3", description="some description 3",
                   price=12.0, stockable=False, user_id=user2.id))
    db.add(Product(id="06e0da01-57fd-2228-95be-0d25c764ea64", name="random product 4", description="some description 4",
                   price=11.0, stockable=True, user_id=user2.id))
    db.add(Product(id="06e0da01-57fd-2228-95be-0d25c764ea65", name="random product 4", description="some description 4",
                   price=11.0, stockable=True, user_id=user2.id))
    
    # coisas a testar:

    db.commit()
    db.close()

def test_post_product_greater_than_five_client():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.post("/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token})

    assert response.status_code == 403, response.text

    data = response.json()
    assert data["detail"] == "Number of products exceeded, please upgrade to premium or delete existing products."

def test_post_product_greater_than_five_premium():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "mariana",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.post("/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token})

    assert response.status_code == 201, response.text

    data = response.json()
    assert data["user_id"] == response.json()["user_id"]
    assert data["name"] == "product1"
    assert data["description"] == "product1's description"
    assert math.isclose(data["price"], 12.5, abs_tol=0.1)
    assert data["stockable"] == True
    assert data["stock"] == 2
    assert data["discount"] == 0
    assert data["categories"] == []
    assert data["image"] == "image1"

def test_change_role_valid():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.put("/user/role" + "/Premium",
                           headers={"Authorization": "Bearer " + token})

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["username"] == "brums21"
    assert data["email"] == "brums21.10@gmail.com"
    assert data["name"] == "Bruna"
    assert data["city"] == "pombal"
    assert data["region"] == "nao existe"
    assert data["photo"] == ""
    assert data["role"] == "Premium"

def test_change_role_invalid():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.put("/user/role" + "/random",
                           headers={"Authorization": "Bearer " + token})

    assert response.status_code == 403, response.text

    data = response.json()
    assert data["detail"] == "User role is not valid. Valid options are: Client and Premium."

def test_change_role_and_put_product_premium_to_client():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.put("/user/role" + "/Premium",
                           headers={"Authorization": "Bearer " + token})

    assert response.status_code == 200, response.text

    response = client.post("/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token})

    assert response.status_code == 201

    response = client.post("/product",
                           json={
                               "name": "product2",
                               "description": "product2's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token})
    
    assert response.status_code == 201

    response = client.put("/user/role" + "/Client",
                           headers={"Authorization": "Bearer " + token})
    
    response = client.post("/product",
                           json={
                               "name": "product2",
                               "description": "product2's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token})
    
    assert response.status_code == 403, response.text

    data = response.json()
    assert data["detail"] == "Number of products exceeded, please upgrade to premium or delete existing products."