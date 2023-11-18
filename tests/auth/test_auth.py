import os
import boto3

from unittest.mock import patch
from auth.user_auth import sign_up_auth, check_email_auth, resend_email_code_auth, sign_in_auth, forgot_password_auth, \
    confirm_forgot_password_auth
from dotenv import load_dotenv

load_dotenv()


def mock_sign_up(ClientId, Username, Password, UserAttributes):
    return {
        'ResponseMetadata': {
            'HTTPStatusCode': 200
        }
    }


@patch('boto3.client')
def test_sign_up_auth(mock_boto3_client):
    mock_boto3_client.return_value.sign_up.side_effect = mock_sign_up

    client = boto3.client('cognito-idp', region_name='us-east-1')
    os.environ['COGNITO_USER_CLIENT_ID'] = 'dummy_cognito_user_client_id'

    username = 'test_username'
    email = 'testuser@example.com'
    password = os.getenv("PASSWORD_CORRECT")

    status_code = sign_up_auth(username, email, password, client)
    assert status_code == 200


def mock_check_email(ClientId, Username, ConfirmationCode):
    return {
        'ResponseMetadata': {
            'HTTPStatusCode': 200
        }
    }


@patch('boto3.client')
def test_check_email_auth(mock_boto3_client):
    mock_boto3_client.return_value.confirm_sign_up.side_effect = mock_check_email

    client = boto3.client('cognito-idp', region_name='us-east-1')
    os.environ['COGNITO_USER_CLIENT_ID'] = 'dummy_cognito_user_client_id'

    username = 'test_username'
    code = '123456'

    status_code = check_email_auth(username, code, client)
    assert status_code == 200


def mock_resend_email(ClientId, Username):
    return {
        'ResponseMetadata': {
            'HTTPStatusCode': 200
        }
    }


@patch('boto3.client')
def test_resend_email_auth(mock_boto3_client):
    mock_boto3_client.return_value.resend_confirmation_code.side_effect = mock_resend_email

    client = boto3.client('cognito-idp', region_name='us-east-1')
    os.environ['COGNITO_USER_CLIENT_ID'] = 'dummy_cognito_user_client_id'

    username = 'test_username'

    status_code = resend_email_code_auth(username, client)
    assert status_code == 200


def mock_sign_in_return_token(ClientId, AuthFlow, AuthParameters):
    return {
        'AuthenticationResult': {
            'AccessToken': 'mock_access_token'
        }
    }


@patch('boto3.client')
def test_sign_in_auth_return_token(mock_boto3_client):
    mock_boto3_client.return_value.initiate_auth.side_effect = mock_sign_in_return_token

    client = boto3.client('cognito-idp', region_name='us-east-1')
    os.environ['COGNITO_USER_CLIENT_ID'] = 'dummy_cognito_user_client_id'

    username = 'test_username'
    password = os.getenv("PASSWORD_CORRECT")

    token = sign_in_auth(username, password, client)
    assert token == 'mock_access_token'


def mock_sign_in_access_token_none(ClientId, AuthFlow, AuthParameters):
    return {
        'AuthenticationResult': {
            'AccessToken': None
        }
    }


@patch('boto3.client')
def test_sign_in_auth_token_none(mock_boto3_client):
    mock_boto3_client.return_value.initiate_auth.side_effect = mock_sign_in_access_token_none

    client = boto3.client('cognito-idp', region_name='us-east-1')
    os.environ['COGNITO_USER_CLIENT_ID'] = 'dummy_cognito_user_client_id'

    username = 'test_username'
    password = os.getenv("PASSWORD_CORRECT")

    token = sign_in_auth(username, password, client)
    assert token is None


def mock_forgot_password(ClientId, Username):
    return {
        'ResponseMetadata': {
            'HTTPStatusCode': 200
        }
    }


@patch('boto3.client')
def test_forgot_password_auth(mock_boto3_client):
    mock_boto3_client.return_value.forgot_password.side_effect = mock_forgot_password

    client = boto3.client('cognito-idp', region_name='us-east-1')
    os.environ['COGNITO_USER_CLIENT_ID'] = 'dummy_cognito_user_client_id'

    username = 'test_username'
    status_code = forgot_password_auth(username, client)
    assert status_code == 200


def mock_confirm_forgot_password(ClientId, Username, ConfirmationCode, Password):
    return {
        'ResponseMetadata': {
            'HTTPStatusCode': 200
        }
    }


@patch('boto3.client')
def test_confirm_forgot_password_auth(mock_boto3_client):
    mock_boto3_client.return_value.confirm_forgot_password.side_effect = mock_confirm_forgot_password

    client = boto3.client('cognito-idp', region_name='us-east-1')
    os.environ['COGNITO_USER_CLIENT_ID'] = 'dummy_cognito_user_client_id'

    username = 'test_username'
    code = '123456'
    password = os.getenv("PASSWORD_CORRECT")

    status_code = confirm_forgot_password_auth(username, code, password, client)
    assert status_code == 200
