import os

import pytest
from starlette.testclient import TestClient

from main import app
from models.user import User
from models.ratingUser import RatingUser
from schemas.ratingUser import CreateRatingUser, UpdateRatingUser
from tests.test_sql_app import TestingSessionLocal
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def load_data():
    db = TestingSessionLocal()
    db.query(User).delete()
    db.query(RatingUser).delete()
    user1 = User(id="06e0da01-57fd-4441-95be-1111111111111", name="Bruna", username="brums21",
                 email="brums21.10@gmail.com", city="pombal",
                 region="nao existe", photo="", role="Client")
    user2 = User(id="06e0da01-57fd-4441-95be-1111111111112", name="Mariana", username="mariana",
                 email="marianaandrade@ua.pt", city="aveiro",
                 region="nao sei", photo="", role="Client")

    db.add(user1)
    db.add(user2)
    db.commit()
    db.close()


def login_user_1():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]
    return token


def login_user_2():
    os.environ['COGNITO_USER_CLIENT_ID'] = '414qtus5nd7veam6tgeqtua9j6'

    response = client.post("/api/auth/sign-in", json={
        "identifier": "mariana",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]
    return token


def test_create_rating_user_success():
    rating = CreateRatingUser(rating=5, rated_user_id="06e0da01-57fd-4441-95be-1111111111112")

    response = client.post("/api/rating-user",
                           json=rating.model_dump(),
                           headers={"Authorization": f"Bearer {login_user_1()}"})

    assert response.status_code == 201
    assert response.json()["rating"] == 5
    assert response.json()["rated_user_id"] == "06e0da01-57fd-4441-95be-1111111111112"
    assert response.json()["user_id"] == "06e0da01-57fd-4441-95be-1111111111111"


def create_rating_user_not_auth():
    rating = CreateRatingUser(rating=5, rated_user_id="06e0da01-57fd-4441-95be-1111111111112")

    response = client.post("/api/rating-user",
                           json=rating.model_dump())

    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_create_rating_rated_user_not_found():
    rating = CreateRatingUser(rating=5, rated_user_id="06e0da01-57fd-4441-95be-1111111111113")

    response = client.post("/api/rating-user",
                           json=rating.model_dump(),
                           headers={"Authorization": f"Bearer {login_user_1()}"})

    assert response.status_code == 404
    assert response.json() == {"detail": "To be rated user not not found"}


def test_create_rating_user_rating_already_exists():
    rating = CreateRatingUser(rating=5, rated_user_id="06e0da01-57fd-4441-95be-1111111111112")

    response = client.post("/api/rating-user",
                           json=rating.model_dump(),
                           headers={"Authorization": f"Bearer {login_user_1()}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "A rating for this user was already created, please edit it instead"}  #TODO: check this


def test_create_rating_user_rating_not_between_0_and_5():
    rating = CreateRatingUser(rating=6, rated_user_id="06e0da01-57fd-4441-95be-1111111111112")

    response = client.post("/api/rating-user",
                           json=rating.model_dump(),
                           headers={"Authorization": f"Bearer {login_user_1()}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "Rating should be between 0 and 5"}


def test_create_rating_user_rating_cannot_rate_yourself():
    rating = CreateRatingUser(rating=5, rated_user_id="06e0da01-57fd-4441-95be-1111111111111")

    response = client.post("/api/rating-user",
                           json=rating.model_dump(),
                           headers={"Authorization": f"Bearer {login_user_1()}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "You can not rate yourself"}





    rating = UpdateRatingUser(rating=3, id="06e0da01-57fd-4441-95be-1111111111112")

    response = client.put("/api/rating-user",
                          json=rating.model_dump(),
                          headers={"Authorization": f"Bearer {login_user_1()}"})

    assert response.status_code == 200
    assert response.json()["rating"] == 3
    assert response.json()["rated_user_id"] == "06e0da01-57fd-4441-95be-1111111111112"
    assert response.json()["user_id"] == "06e0da01-57fd-4441-95be-1111111111111"


def test_put_user_rating_user_rated_not_found():
    rating = UpdateRatingUser(rating=3, id="06e0da01-57fd-4441-95be-1111111111113")

    response = client.put("/api/rating-user",
                          json=rating.model_dump(),
                          headers={"Authorization": f"Bearer {login_user_1()}"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Rated user not found"}


def test_put_user_rating_rating_not_found():
    rating = UpdateRatingUser(rating=3, id="06e0da01-57fd-4441-95be-1111111111112")

    response = client.put("/api/rating-user",
                          json=rating.model_dump(),
                          headers={"Authorization": f"Bearer {login_user_2()}"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Rating not found"}


def test_put_user_rating_rating_not_between_0_and_5():
    rating = UpdateRatingUser(rating=6, id="06e0da01-57fd-4441-95be-1111111111112")

    response = client.put("/api/rating-user",
                          json=rating.model_dump(),
                          headers={"Authorization": f"Bearer {login_user_1()}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "Rating should be between 0 and 5"}


def test_put_user_rating_not_auth():
    rating = UpdateRatingUser(rating=6, id="06e0da01-57fd-4441-95be-1111111111112")

    response = client.put("/api/rating-user",
                          json=rating.model_dump())

    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}
