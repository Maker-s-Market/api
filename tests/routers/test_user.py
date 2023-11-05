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
load_dotenv()

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
    response = client.get("/auth/current-user")
    assert response.status_code == 403
    assert response.json() == {'detail': 'Not authenticated'}


def test_get_current_user_logged():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": str(os.getenv("PASSWORD_CORRECT"))
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.get("/auth/current-user", headers={"Authorization": "Bearer " + token})
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
    response = client.put("/user", json={
        "id": update.id,
        "name": update.name,
        "city": update.city,
        "region": update.region,
        "photo": update.photo
    })

    assert response.status_code == 403
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_user_sucess():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.get("/auth/current-user", headers={"Authorization": "Bearer " + token})
    assert response.status_code == 200

    update = UserUpdate(id=response.json()["id"], name="Bruna update", city="pombal", region="Leiria", photo="")
    response = client.put("/user", json={
        "id": update.id,
        "name": update.name,
        "city": update.city,
        "region": update.region,
        "photo": update.photo
    }, headers={"Authorization": "Bearer " + token})

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "brums21"
    assert data["name"] == "Bruna update"
    assert data["city"] == "pombal"
    assert data["region"] == "Leiria"
    assert data["photo"] == ""

def test_update_user_not_the_owner():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.get("/auth/current-user", headers={"Authorization": "Bearer " + token})
    assert response.status_code == 200

    update = UserUpdate(id="1234567", name="Bruna update", city="pombal", region="Leiria", photo="")
    response = client.put("/user", json={
        "id": update.id,
        "name": update.name,
        "city": update.city,
        "region": update.region,
        "photo": update.photo
    }, headers={"Authorization": "Bearer " + token})

    assert response.status_code == 403
    assert response.json() == {'detail': 'You can only update your own user'}


