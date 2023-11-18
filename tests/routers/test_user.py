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
    user1 = User(id=str(uuid4()), name="Bruna", username="brums21", email="brums21.10@gmail.com", city="pombal",
                 region="nao existe", photo="", role="Client")
    user2 = User(id=str(uuid4()), name="Mariana", username="mariana", email="marianaandrade@ua.pt", city="aveiro",
                 region="nao sei", photo="", role="Client")
    new_user(user1, db)
    new_user(user2, db)
    db.commit()
    db.close()


def test_get_current_user_not_logged():
    response = client.get(AUTH_CURRENT_USER)
    assert response.status_code == 403
    assert response.json() == {'detail': 'Not authenticated'}


def test_get_current_user_logged():

    response = client.post(AUTH_SIGN_IN, json={
        "identifier": "brums21",
        "password": str(os.getenv("PASSWORD_CORRECT"))
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.get(AUTH_CURRENT_USER, headers={"Authorization": BEARER + token})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "brums21"
    assert data["email"] == "brums21.10@gmail.com"
    assert data["role"] == "Client"
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


def test_update_user_sucess():

    response = client.post(AUTH_SIGN_IN, json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.get(AUTH_CURRENT_USER, headers={"Authorization": BEARER + token})
    assert response.status_code == 200

    update = UserUpdate(id=response.json()["id"], name="UPDATE_BRUNA", city="pombal", region="Leiria", photo="")
    response = client.put(USER, json={
        "id": update.id,
        "name": update.name,
        "city": update.city,
        "region": update.region,
        "photo": update.photo
    }, headers={"Authorization": BEARER + token})

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "brums21"
    assert data["name"] == "UPDATE_BRUNA"
    assert data["city"] == "pombal"
    assert data["region"] == "Leiria"
    assert data["photo"] == ""


def test_update_user_not_the_owner():

    response = client.post(AUTH_SIGN_IN, json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.get(AUTH_CURRENT_USER, headers={"Authorization": BEARER + token})
    assert response.status_code == 200

    update = UserUpdate(id="1234567", name="UPDATE_BRUNA", city="pombal", region="Leiria", photo="")
    response = client.put(USER, json={
        "id": update.id,
        "name": update.name,
        "city": update.city,
        "region": update.region,
        "photo": update.photo
    }, headers={"Authorization": BEARER + token})

    assert response.status_code == 403
    assert response.json() == {'detail': 'You can only update your own user'}
