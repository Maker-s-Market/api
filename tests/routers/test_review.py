import os

import pytest
from uuid import uuid4

from starlette.testclient import TestClient

from main import app
from models.category import Category
from models.product import Product
from models.review import Review
from models.user import User
from tests.test_sql_app import TestingSessionLocal
from dotenv import load_dotenv

load_dotenv() #import pytest.ini env variables

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def load_data():
    db = TestingSessionLocal()
    db.query(Category).delete()
    db.query(Product).delete()
    db.query(Review).delete()
    db.query(User).delete()
    user1 = User(id="06e0da01-57fd-4441-95be-1111111111111",name="Bruna", username="brums21", email="brums21.10@gmail.com", city="pombal",
                 region="nao existe", photo="", role="Client")
    user2 = User(id="06e0da01-57fd-4441-95be-1111111111112", name="Mariana", username="mariana", email="marianaandrade@ua.pt", city="aveiro",
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

    db.add(Review(id="06e0da01-57fd-2229-95be-123455555567", text="some comment1", user_id=user1.id,
                  product_id="06e0da01-57fd-2228-95be-0d25c764ea57"))

    db.add(Review(id="06e0da01-57fd-2229-95be-123455555568", text="some comment2", user_id=user2.id,
                  product_id="06e0da01-57fd-2228-95be-0d25c764ea57"))

    db.add(Review(id="06e0da01-57fd-2229-95be-123455555569", text="some comment3", user_id=user2.id,
                  product_id="06e0da01-57fd-2229-95be-123455555566"))
    db.commit()
    db.close()


def test_get_reviews():
    response = client.get("/review/06e0da01-57fd-2229-95be-123455555566")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["review"]["text"] == "some comment3"
    assert data[0]["user"]["username"] == "mariana"


def test_create_review_not_auth():
    response = client.post("/review",
                           json={"text": "some comment", "product_id": "06e0da01-57fd-2228-95be-0d25c764ea57"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_create_review_success():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.post("/review",
                           json={"text": "some comment", "product_id": "06e0da01-57fd-2228-95be-0d25c764ea57"},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201

    response = client.get("/review/06e0da01-57fd-2228-95be-0d25c764ea57")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[2]["review"]["text"] == "some comment"
    assert data[2]["user"]["username"] == "brums21"


def test_delete_review_not_auth():
    response = client.delete("/review/06e0da01-57fd-2229-95be-123455555567")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_delete_review_success():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.delete("/review/06e0da01-57fd-2229-95be-123455555567",
                             headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Review deleted succesfully"}


def test_delete_review_not_found():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.delete("/review/123456",
                             headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    assert response.json() == {"detail": "No review found with that id"}


def test_delete_review_not_owner():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.delete("/review/06e0da01-57fd-2229-95be-123455555568",
                             headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "Only the user can delete its reviews"}


def test_put_review_update_invalid_review_id():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.put("/review",
                          json={
                              "id": "06e0da01-57fd-2229-95be-123455555567",
                              "text": "review random text",
                              "product_id": "06e0da01-57fd-2228-95be-0d25c764ea57"
                          },
                          headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    assert response.json() == {'detail': 'No review found with that id'}


def test_put_review_update_no_auth():
    response = client.put("/review",
                          json={
                              "id": "06e0da01-57fd-2229-95be-123455555568",
                              "text": "review random text",
                              "product_id": "06e0da01-57fd-2228-95be-0d25c764ea57"
                          })

    assert response.status_code == 403
    assert response.json() == {'detail': 'Not authenticated'}


def test_put_review_user_not_review_owner():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.put("/review",
                          json={
                              "id": "06e0da01-57fd-2229-95be-123455555568",
                              "text": "review random text",
                              "product_id": "06e0da01-57fd-2228-95be-0d25c764ea57"
                          },
                          headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json() == {'detail': 'Only the user can update its reviews'}


def test_put_review_success():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "mariana",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.put("/review",
                          json={"id": "06e0da01-57fd-2229-95be-123455555568",
                                "text": "some comment updated",
                                "product_id": "06e0da01-57fd-2228-95be-0d25c764ea57"},
                          headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()

    assert data["text"] == "some comment updated"
    assert data["product_id"] == "06e0da01-57fd-2228-95be-0d25c764ea57"
    assert data["user_id"] == "06e0da01-57fd-4441-95be-1111111111112"


def test_get_my_reviews_not_auth():
    response = client.get("/review")
    assert response.status_code == 403
    assert response.json() == {'detail': 'Not authenticated'}


def test_get_my_reviews_success():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "mariana",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.get("/review", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    assert data[0]["text"] == "some comment updated"
    assert data[0]["product_id"] == "06e0da01-57fd-2228-95be-0d25c764ea57"
    assert data[0]["user_id"] == "06e0da01-57fd-4441-95be-1111111111112"

    assert data[1]["text"] == "some comment3"
    assert data[1]["product_id"] == "06e0da01-57fd-2229-95be-123455555566"
    assert data[1]["user_id"] == "06e0da01-57fd-4441-95be-1111111111112"






