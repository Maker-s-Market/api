import os

import pytest

from starlette.testclient import TestClient
from main import app
from models.user import User
from schemas.user import UserUpdate
from repositories.userRepo import new_user
from tests.test_sql_app import TestingSessionLocal
from uuid import uuid4
from dotenv import load_dotenv

client = TestClient(app)

AUTH_CURRENT_USER = "/auth/me"
AUTH_SIGN_IN = "/auth/sign-in"
BEARER = "Bearer "
USER = "/user"
UPDATE_BRUNA = "Bruna update"


@pytest.fixture(scope="module", autouse=True)
def load_data():
    db = TestingSessionLocal()
    db.query(User).delete()
    user1 = User(id="682d9204-9be4-4897-aafc-fe89b3f35183", name="Bruna", username="brums21",
                 email="brums21.10@gmail.com", city="pombal",
                 region="nao existe", photo="", role="Client")
    user2 = User(id="7fbae594-be16-4803-99b1-4c6a3b023bff", name="Mariana", username="mariana",
                 email="marianaandrade@ua.pt", city="aveiro",
                 region="nao sei", photo="", role="Client")
    db.add(user1)
    db.add(user2)
    db.commit()
    db.close()


def login_user_1():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]
    return token


def test_get_current_user_not_logged():
    response = client.get(AUTH_CURRENT_USER)
    assert response.status_code == 403
    assert response.json() == {'detail': 'Not authenticated'}


def test_get_current_user_logged():
    response = client.get(AUTH_CURRENT_USER, headers={"Authorization": BEARER + login_user_1()})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "brums21"
    assert data["email"] == "brums21.10@gmail.com"
    assert data["name"] == "Bruna"
    assert data["city"] == "pombal"
    assert data["region"] == "nao existe"
    assert data["photo"] == ""


def test_update_user_not_logged():
    update = UserUpdate(id="1234567", name="Bruna", city="pombal", region="Leiria", photo="")
    response = client.put(USER, json={
        "id": update.id,
        "name": update.name,
        "city": update.city,
        "region": update.region,
        "photo": update.photo
    })

    assert response.status_code == 403
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_user_success():

    response = client.get(AUTH_CURRENT_USER, headers={"Authorization": BEARER + login_user_1()})
    assert response.status_code == 200

    update = UserUpdate(id=response.json()["id"], name="UPDATE_BRUNA", city="pombal", region="Leiria", photo="")
    response = client.put(USER, json={
        "id": update.id,
        "name": update.name,
        "city": update.city,
        "region": update.region,
        "photo": update.photo
    }, headers={"Authorization": BEARER + login_user_1()})

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "brums21"
    assert data["name"] == "UPDATE_BRUNA"
    assert data["city"] == "pombal"
    assert data["region"] == "Leiria"
    assert data["photo"] == ""


def test_update_user_not_the_owner():
    response = client.get(AUTH_CURRENT_USER, headers={"Authorization": BEARER + login_user_1()})
    assert response.status_code == 200

    update = UserUpdate(id="1234567", name="UPDATE_BRUNA", city="pombal", region="Leiria", photo="")
    response = client.put(USER, json={
        "id": update.id,
        "name": update.name,
        "city": update.city,
        "region": update.region,
        "photo": update.photo
    }, headers={"Authorization": BEARER + login_user_1()})

    assert response.status_code == 403
    assert response.json() == {'detail': 'You can only update your own user'}


def test_follow_success():
    response = client.get(AUTH_CURRENT_USER, headers={"Authorization": BEARER + login_user_1()})
    assert response.status_code == 200

    response = client.post("/user/follow-seller/7fbae594-be16-4803-99b1-4c6a3b023bff",
                           headers={"Authorization": BEARER + login_user_1()})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "brums21"
    assert len(data["followed"]) == 1
    assert data["followed"][0]["username"] == "mariana"


def test_follow_already_following():
    response = client.get(AUTH_CURRENT_USER, headers={"Authorization": BEARER + login_user_1()})
    assert response.status_code == 200

    response = client.post("/user/follow-seller/7fbae594-be16-4803-99b1-4c6a3b023bff",
                           headers={"Authorization": BEARER + login_user_1()})
    assert response.status_code == 403
    assert response.json() == {'detail': 'Already following this user/seller'}


def test_follow_not_found():
    response = client.get(AUTH_CURRENT_USER, headers={"Authorization": BEARER + login_user_1()})
    assert response.status_code == 200

    response = client.post("/user/follow-seller/1234567",
                           headers={"Authorization": BEARER + login_user_1()})
    assert response.status_code == 404
    assert response.json() == {'detail': 'Seller not found'}


def test_follow_yourself():
    response = client.get(AUTH_CURRENT_USER, headers={"Authorization": BEARER + login_user_1()})
    assert response.status_code == 200

    response = client.post("/user/follow-seller/682d9204-9be4-4897-aafc-fe89b3f35183",
                           headers={"Authorization": BEARER + login_user_1()})
    assert response.status_code == 403
    assert response.json() == {'detail': 'You can not follow yourself'}


def test_follow_not_logged():
    response = client.post("/user/follow-seller/682d9204-9be4-4897-aafc-fe89b3f35183")
    assert response.status_code == 403
    assert response.json() == {'detail': 'Not authenticated'}


