import pytest
import unittest
import os

from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from models.user import User
from repositories.userRepo import new_user
from schemas.user import CreateUser, ActivateUser, UserIdentifier, ChangePassword, UserLogin
from tests.test_sql_app import TestingSessionLocal
from dotenv import load_dotenv

load_dotenv()

LINK_SIGN_UP = 'routers.auth.sign_up_auth'
LINK_SIGN_IN = 'routers.auth.sign_in_auth'
LINK_CONFIRM_PASSWORD = 'routers.auth.confirm_forgot_password_auth'
LINK_RESEND_EMAIL_CODE = 'routers.auth.resend_email_code_auth'

SIGN_UP_DIR = "/auth/sign-up"
SIGN_IN_DIR = "/auth/sign-in"
CONFIRM_PASSWORD_DIR = "/auth/confirm-forgot-password"
RESEND_EMAIL_CODE = "/auth/resend-email-code"


USERNAME_TEST = "user name test"
RANDOM_EMAIL = "randomemail@email.com"
MARIA_EMAIL = "maria@email.com"

@pytest.fixture(scope="module", autouse=True)
def load_data():
    db = TestingSessionLocal()
    db.query(User).delete()
    user = CreateUser(
        name="maria",
        username="maria123",
        email=MARIA_EMAIL,
        password=os.getenv("PASSWORD_CORRECT"),
        city="city",
        region="region",
        photo="photo",
    )
    new_user(user, db)
    db.commit()
    db.close()


class TestAuthRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_sign_up_success(self):
        with patch(LINK_SIGN_UP, return_value=200):
            create_user = CreateUser(
                name="USERNAME_TEST",
                username="usertest1",
                email=RANDOM_EMAIL,
                password=os.getenv("PASSWORD_CORRECT"),
                city="city",
                region="region",
                photo="photo",
            )

            response = self.client.post(SIGN_UP_DIR, json={
                "name": create_user.name,
                "username": create_user.username,
                "email": create_user.email,
                "password": create_user.password,
                "city": create_user.city,
                "region": create_user.region,
                "photo": create_user.photo
            })

            self.assertEqual(response.status_code, 201)  # Adjust this based on your expected status code
            self.assertEqual(response.json(), {"message": "User created"})

    def test_sign_up_user_already_exists(self):
        with patch(LINK_SIGN_UP, return_value=200):
            create_user = CreateUser(
                name="USERNAME_TEST",
                username="usertest1",
                email=RANDOM_EMAIL,
                password=os.getenv("PASSWORD_CORRECT"),
                city="city",
                region="region",
                photo="photo",
            )

            response = self.client.post(SIGN_UP_DIR, json={
                "name": create_user.name,
                "username": create_user.username,
                "email": create_user.email,
                "password": create_user.password,
                "city": create_user.city,
                "region": create_user.region,
                "photo": create_user.photo
            })

            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {"detail": "User already exists in database"})

    def test_sign_up_invalid_password(self):

        with patch(LINK_SIGN_UP, return_value=200):
            create_user = CreateUser(
                name="USERNAME_TEST",
                username="usertest1",
                email=RANDOM_EMAIL,
                password=os.getenv("PASSWORD_INCORRECT"),
                city="city",
                region="region",
                photo="photo",
            )

            response = self.client.post(SIGN_UP_DIR, json={
                "name": create_user.name,
                "username": create_user.username,
                "email": create_user.email,
                "password": create_user.password,
                "city": create_user.city,
                "region": create_user.region,
                "photo": create_user.photo
            })

            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {"detail": "Password does not meet requirements"})

    def test_sign_up_fail(self):
        with patch(LINK_SIGN_UP, return_value=406):
            create_user = CreateUser(
                name="USERNAME_TEST",
                username="usertest1",
                email=RANDOM_EMAIL,
                password=os.getenv("PASSWORD_CORRECT"),
                city="city",
                region="region",
                photo="photo",
            )

            response = self.client.post(SIGN_UP_DIR, json={
                "name": create_user.name,
                "username": create_user.username,
                "email": create_user.email,
                "password": create_user.password,
                "city": create_user.city,
                "region": create_user.region,
                "photo": create_user.photo
            })

            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {"detail": "Couldn't sign up"})

    def test_verify_email_success(self):
        with patch('routers.auth.check_email_auth', return_value=200):
            activate_user = ActivateUser(
                username="usertest1",
                code="123456"
            )

            response = self.client.post("/auth/verify-email", json={
                "username": activate_user.username,
                "code": activate_user.code
            })

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Email confirmed"})

    def test_verify_email_fail(self):
        with patch('routers.auth.check_email_auth', return_value=406):
            activate_user = ActivateUser(
                username="usertest1",
                code="123456"
            )

            response = self.client.post("/auth/verify-email", json={
                "username": activate_user.username,
                "code": activate_user.code
            })

            self.assertEqual(response.status_code, 406)
            self.assertEqual(response.json(), {"detail": "Unable to confirm access, resend a code"})

    def test_confirm_forgot_password_success(self):

        with patch(LINK_CONFIRM_PASSWORD, return_value=200):
            activate_user = ChangePassword(
                identifier="usertest1",
                password=os.getenv("PASSWORD_CORRECT"),
                code="123456"
            )

            response = self.client.post(CONFIRM_PASSWORD_DIR, json={
                "identifier": activate_user.identifier,
                "password": activate_user.password,
                "code": activate_user.code
            })

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Password changed successfully"})

    def test_confirm_forgot_password_invalid_password(self):
        with patch(LINK_CONFIRM_PASSWORD, return_value=200):
            activate_user = ChangePassword(
                identifier="usertest1",
                password=os.getenv("PASSWORD_INCORRECT"),
                code="123456"
            )

            response = self.client.post(CONFIRM_PASSWORD_DIR, json={
                "identifier": activate_user.identifier,
                "password": activate_user.password,
                "code": activate_user.code
            })

            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {"detail": "Password does not meet requirements"})

    def test_confirm_forgot_password_fail(self):

        with patch(LINK_CONFIRM_PASSWORD, return_value=406):
            activate_user = ChangePassword(
                identifier="usertest1",
                password=os.getenv("PASSWORD_CORRECT"),
                code="123456"
            )

            response = self.client.post(CONFIRM_PASSWORD_DIR, json={
                "identifier": activate_user.identifier,
                "password": activate_user.password,
                "code": activate_user.code
            })

            self.assertEqual(response.status_code, 406)
            self.assertEqual(response.json(), {"detail": "Couldn't change the password, try again later"})

    def test_sign_in_success(self):
        with patch(LINK_SIGN_IN, return_value="token Success"):
            user_login = UserLogin(
                identifier="usertest1",
                password=os.getenv("PASSWORD_CORRECT")
            )

            response = self.client.post(SIGN_IN_DIR, json={
                "identifier": user_login.identifier,
                "password": user_login.password
            })

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"token": "token Success"})

    def test_sign_in_fail(self):
        with patch(LINK_SIGN_IN, return_value=None):
            user_login = UserLogin(
                identifier="usertest1",
                password=os.getenv("PASSWORD_CORRECT")
            )

            response = self.client.post(SIGN_IN_DIR, json={
                "identifier": user_login.identifier,
                "password": user_login.password
            })

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {"detail": "Error loging in..."})

    def test_forgot_password_success(self):

        with patch('routers.auth.forgot_password_auth', return_value=200):
            user_identifier = UserIdentifier(
                identifier="usertest1",
            )

            response = self.client.post("/auth/forgot-password", json={
                "identifier": user_identifier.identifier,
            })

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Sent code to email"})

    def test_forgot_password_fail(self):
        with patch('routers.auth.forgot_password_auth', return_value=406):
            user_identifier = UserIdentifier(
                identifier="usertest1",
            )

            response = self.client.post("/auth/forgot-password", json={
                "identifier": user_identifier.identifier,
            })

            self.assertEqual(response.status_code, 406)
            self.assertEqual(response.json(), {"detail": "Couldn't send the code, try again later"})

    def test_resend_email_code_the_user_not_found(self):

        with patch(LINK_RESEND_EMAIL_CODE, return_value=404):
            user_identifier = UserIdentifier(
                identifier="usertest1",
            )

            response = self.client.post(RESEND_EMAIL_CODE, json={
                "identifier": user_identifier.identifier,
            })

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {"detail": "User not found"})

    def test_resend_email_code_success(self):
        with patch(LINK_RESEND_EMAIL_CODE, return_value=200):

            user_identifier = UserIdentifier(
                identifier="maria@email.com",
            )

            response = self.client.post(RESEND_EMAIL_CODE, json={
                "identifier": user_identifier.identifier,
            })

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Code resent successfully"})

    def test_resend_email_code_fail(self):

        with patch(LINK_RESEND_EMAIL_CODE, return_value=406):
            user_identifier = UserIdentifier(
                identifier="maria@email.com",
            )

            response = self.client.post(RESEND_EMAIL_CODE, json={
                "identifier": user_identifier.identifier,
            })

            self.assertEqual(response.status_code, 406)
            self.assertEqual(response.json(), {"detail": "Couldn't send the code, try again later"})

