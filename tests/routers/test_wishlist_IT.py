import os

import pytest

from starlette.testclient import TestClient

from main import app
from dotenv import load_dotenv

from models.category import Category
from models.product import Product
from models.user import User
from models.wishList import Wishlist
from tests.test_sql_app import TestingSessionLocal

load_dotenv()

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def load_data():
    db = TestingSessionLocal()
    db.query(User).delete()
    db.query(Category).delete()
    db.query(Product).delete()
    db.query(Wishlist).delete()

    user2 = User(id="06e0da01-57fd-4441-95be-1111111111112", name="Mariana", username="mariana",
                 email="marianaandrade@ua.pt", city="aveiro",
                 region="nao sei", photo="", role="Client")
    db.add(user2)
    db.add(Category(id="06e0da01-57fd-4441-95be-0d25c764ea57", name="Category1x", icon="icon1", slug="category1x"))
    product1 = Product(id="06e0da01-57fd-2228-95be-0d25c764ea57", name="random product 2",
                       description="some description 2",
                       price=11.0, stockable=True, user_id=user2.id)
    db.add(product1)

    db.add(Product(id="06e0da01-57fd-2229-95be-123455555566", name="random product 3", description="some description 3",
                   price=10.0, stockable=True, user_id="123456789023456789"))

    wishlist_the_user = Wishlist(id="06e0da01-57fd-4441-95be-1111111111111", products=[product1])
    db.add(wishlist_the_user)

    user1 = User(id="06e0da01-57fd-4441-95be-1111111111111", name="Bruna", username="brums21",
                 email="brums21.10@gmail.com", city="pombal",
                 region="nao existe", photo="", role="Client", wishlist_id=wishlist_the_user.id)
    db.add(user1)
    db.add(Product(id="06e0da01-57fd-2227-95be-0d25c764ea56", name="random product 1", description="some description 1",
                   price=12.0, stockable=False, user_id=user1.id))

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


def test_get_user_wishlist_success():
    token = login_user1()
    response = client.get("/wishlist", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "06e0da01-57fd-4441-95be-1111111111111"
    assert len(data["products"]) == 1
    assert data["products"][0]["id"] == "06e0da01-57fd-2228-95be-0d25c764ea57"


def test_get_user_wishlist_fail_not_initialized():
    token = login_user2()
    response = client.get("/wishlist", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Wishlist was not initialized"


def test_get_user_wishlist_not_auth():
    response = client.get("/wishlist")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_add_product_to_wishlist_success():
    token = login_user1()
    response = client.post(
        "/wishlist/06e0da01-57fd-2229-95be-123455555566",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "06e0da01-57fd-4441-95be-1111111111111"
    assert len(data["products"]) == 2
    assert data["products"][0]["id"] == "06e0da01-57fd-2228-95be-0d25c764ea57"
    assert data["products"][1]["id"] == "06e0da01-57fd-2229-95be-123455555566"


def test_add_product_to_wishlist_fail_already_in_wishlist():
    token = login_user1()
    response = client.post(
        "/wishlist/06e0da01-57fd-2228-95be-0d25c764ea57",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Product already in wishlist"


def test_add_product_to_wishlist_fail_own_product():
    token = login_user1()
    response = client.post(
        "/wishlist/06e0da01-57fd-2227-95be-0d25c764ea56",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "You can't add your own products to the wishlist"


def test_add_product_to_wishlist_fail_not_found():
    token = login_user1()
    response = client.post(
        "/wishlist/id_not_exists",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Product not found"
