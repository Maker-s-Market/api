import os

import pytest

from starlette.testclient import TestClient
from main import app
from models.user import User
from repositories.userRepo import new_user
from tests.test_sql_app import TestingSessionLocal
from uuid import uuid4

client = TestClient(app)


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
        "password": "Pass123!"
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



