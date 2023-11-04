import pytest
import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from main import app
from models.user import User
from schemas.user import CreateUser, ActivateUser, UserIdentifier, ChangePassword
from tests.test_sql_app import TestingSessionLocal


@pytest.fixture(scope="module", autouse=True)
def load_data():
    db = TestingSessionLocal()
    db.query(User).delete()
    db.commit()
    db.close()


class TestAuthRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_sign_up_success(self):
        mock_cognito = Mock()
        mock_cognito.return_value.sign_up = 200
        mock_cognito.exceptions.UsernameExistsException = Exception
        mock_cognito.exceptions.InvalidPasswordException = Exception
        mock_cognito.exceptions.ClientError = Exception

        with patch('routers.auth.sign_up_auth', return_value=200):
            create_user = CreateUser(
                name="user name test",
                username="usertest1",
                email="randomemail@email.com",
                password="Pass123!",
                city="random city",
                region="random region",
                photo="random photo",
            )

            response = self.client.post("/auth/sign-up", json={
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
        mock_cognito = Mock()
        mock_cognito.return_value.sign_up = 200
        mock_cognito.exceptions.UsernameExistsException = Exception
        mock_cognito.exceptions.InvalidPasswordException = Exception
        mock_cognito.exceptions.ClientError = Exception

        with patch('routers.auth.sign_up_auth', return_value=200):
            create_user = CreateUser(
                name="user name test",
                username="usertest1",
                email="randomemail@email.com",
                password="Pass123!",
                city="random city",
                region="random region",
                photo="random photo",
            )

            response = self.client.post("/auth/sign-up", json={
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
        mock_cognito = Mock()
        mock_cognito.return_value.sign_up = 200
        mock_cognito.exceptions.UsernameExistsException = Exception
        mock_cognito.exceptions.InvalidPasswordException = Exception
        mock_cognito.exceptions.ClientError = Exception

        with patch('routers.auth.sign_up_auth', return_value=200):
            create_user = CreateUser(
                name="user name test",
                username="usertest1",
                email="randomemail@.com",
                password="pass",
                city="random city",
                region="random region",
                photo="random photo",
            )

            response = self.client.post("/auth/sign-up", json={
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

    def test_verify_email_success(self):
        mock_cognito = Mock()
        mock_cognito.return_value.check_email_auth = 200
        mock_cognito.exceptions.UsernameExistsException = Exception
        mock_cognito.exceptions.InvalidPasswordException = Exception
        mock_cognito.exceptions.ClientError = Exception

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

    def test_confirm_forgot_password_success(self):
        mock_cognito = Mock()
        mock_cognito.return_value.confirm_forgot_password = 200
        mock_cognito.exceptions.UsernameExistsException = Exception
        mock_cognito.exceptions.InvalidPasswordException = Exception
        mock_cognito.exceptions.ClientError = Exception

        with patch('routers.auth.confirm_forgot_password_auth', return_value=200):
            activate_user = ChangePassword(
                identifier="usertest1",
                password="Pass123!",
                code="123456"
            )

            response = self.client.post("/auth/confirm-forgot-password", json={
                "identifier": activate_user.identifier,
                "password": activate_user.password,
                "code": activate_user.code
            })

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Password changed successfully"})

    def test_confirm_forgot_password_invalid_password(self):
        mock_cognito = Mock()
        mock_cognito.return_value.confirm_forgot_password = 200
        mock_cognito.exceptions.UsernameExistsException = Exception
        mock_cognito.exceptions.InvalidPasswordException = Exception
        mock_cognito.exceptions.ClientError = Exception

        with patch('routers.auth.confirm_forgot_password_auth', return_value=200):
            activate_user = ChangePassword(
                identifier="usertest1",
                password="pass",
                code="123456"
            )

            response = self.client.post("/auth/confirm-forgot-password", json={
                "identifier": activate_user.identifier,
                "password": activate_user.password,
                "code": activate_user.code
            })

            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {"detail": "Password does not meet requirements"})
