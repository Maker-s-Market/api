import os

import pytest

from starlette.testclient import TestClient

from main import app
from models.category import Category
from models.product import Product
from models.ratingProduct import RatingProduct
from models.user import User
from schemas.ratingProduct import CreateRatingProduct, UpdateRatingProduct
from tests.test_sql_app import TestingSessionLocal
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def load_data():
    db = TestingSessionLocal()
    db.query(Category).delete()
    db.query(Product).delete()
    db.query(RatingProduct).delete()
    db.query(User).delete()
    user1 = User(id="06e0da01-57fd-4441-95be-1111111111111", name="Bruna", username="brums21",
                 email="brums21.10@gmail.com", city="pombal",
                 region="nao existe", photo="", role="Client")
    user2 = User(id="06e0da01-57fd-4441-95be-1111111111112", name="Mariana", username="mariana",
                 email="marianaandrade@ua.pt", city="aveiro",
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

    db.add(
        RatingProduct(id="06e0da01-57fd-2227-95be-0d25c764ea56", rating=4,
                      product_id="06e0da01-57fd-2227-95be-0d25c764ea56",
                      user_id=user2.id))
    db.commit()
    db.close()


def login_user1():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]
    return token


def login_user2():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "mariana",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]
    return token


def test_create_rating_success():
    token = login_user1()
    rating = CreateRatingProduct(rating=4,
                                 product_id="06e0da01-57fd-2228-95be-0d25c764ea57",
                                 user_id="06e0da01-57fd-4441-95be-1111111111111")
    response = client.post("/rating-product",
                           json=rating.model_dump(),
                           headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 4
    assert data["product_id"] == "06e0da01-57fd-2228-95be-0d25c764ea57"
    assert data["user_id"] == "06e0da01-57fd-4441-95be-1111111111111"


def test_create_rating_not_auth():
    rating = CreateRatingProduct(rating=4,
                                 product_id="06e0da01-57fd-2227-95be-0d25c764ea56",
                                 user_id="06e0da01-57fd-4441-95be-1111111111111")
    response = client.post("/rating-product",
                           json=rating.model_dump())

    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_create_rating_product_not_found():
    token = login_user1()
    rating = CreateRatingProduct(rating=4,
                                 product_id="id_not_exists",
                                 user_id="06e0da01-57fd-4441-95be-1111111111111")
    response = client.post("/rating-product",
                           json=rating.model_dump(),
                           headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_create_rating_own_product():
    token = login_user1()
    rating = CreateRatingProduct(rating=4,
                                 product_id="06e0da01-57fd-2227-95be-0d25c764ea56",
                                 user_id="06e0da01-57fd-4441-95be-1111111111111")
    response = client.post("/rating-product",
                           json=rating.model_dump(),
                           headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "You can't rate your own product"}


def test_create_rating_not_in_range():
    token = login_user1()
    rating = CreateRatingProduct(rating=6,
                                 product_id="06e0da01-57fd-2228-95be-0d25c764ea57",
                                 user_id="06e0da01-57fd-4441-95be-1111111111111")
    response = client.post("/rating-product",
                           json=rating.model_dump(),
                           headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "Rating should be between 1 and 5"}


def test_create_rating_already_exists():
    token = login_user1()
    rating = CreateRatingProduct(rating=4,
                                 product_id="06e0da01-57fd-2228-95be-0d25c764ea57",
                                 user_id="06e0da01-57fd-4441-95be-1111111111112")
    response = client.post("/rating-product",
                           json=rating.model_dump(),
                           headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "A rating for this product was already created, please edit it instead"}


def test_update_rating_success():
    login_user2()
    upd_rating = UpdateRatingProduct(id="06e0da01-57fd-2227-95be-0d25c764ea56", rating=5)
    response = client.put("/rating-product",
                          json=upd_rating.model_dump(),
                          headers={"Authorization": f"Bearer {login_user2()}"})

    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 5
    assert data["product_id"] == "06e0da01-57fd-2227-95be-0d25c764ea56"
    assert data["user_id"] == "06e0da01-57fd-4441-95be-1111111111112"


def test_update_rating_not_auth():
    upd_rating = UpdateRatingProduct(id="06e0da01-57fd-2227-95be-0d25c764ea56", rating=5)
    response = client.put("/rating-product",
                          json=upd_rating.model_dump())

    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_update_rating_not_found():
    upd_rating = UpdateRatingProduct(id="id_not_exists", rating=5)
    response = client.put("/rating-product",
                          json=upd_rating.model_dump(),
                          headers={"Authorization": f"Bearer {login_user2()}"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Rating not found"}


def test_update_rating_not_owner():
    upd_rating = UpdateRatingProduct(id="06e0da01-57fd-2227-95be-0d25c764ea56", rating=5)
    response = client.put("/rating-product",
                          json=upd_rating.model_dump(),
                          headers={"Authorization": f"Bearer {login_user1()}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "You are not the user who made this review. "
                                         "Only the owner of the review can delete it."}


def test_update_rating_not_in_range():
    upd_rating = UpdateRatingProduct(id="06e0da01-57fd-2227-95be-0d25c764ea56", rating=0)
    response = client.put("/rating-product",
                          json=upd_rating.model_dump(),
                          headers={"Authorization": f"Bearer {login_user2()}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "Rating should be between 1 and 5"}
