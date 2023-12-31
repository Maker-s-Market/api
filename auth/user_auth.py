import os

import boto3
import botocore
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", '.aws')
load_dotenv(env_path)

cognito_client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION'))


def sign_up_auth(username: str, email: str, password: str, client: botocore.client.BaseClient = cognito_client):
    """
        function that puts a user in the AWS user pool and sends an email with a 1 time code 
    """

    response = client.sign_up(
        ClientId=os.getenv('COGNITO_USER_CLIENT_ID'),
        Username=username,
        Password=password,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': email,
            }

        ]
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']

    return status_code


def check_email_auth(username: str, code: str, client: botocore.client.BaseClient = cognito_client):
    """
        function that checks if the code provided by email is correct or not
    """

    response = client.confirm_sign_up(
        ClientId=os.getenv('COGNITO_USER_CLIENT_ID'),
        Username=username,
        ConfirmationCode=code
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    
    return status_code


def resend_email_code_auth(username: str, client: botocore.client.BaseClient = cognito_client):
    """
        resends the confirmation code to the specified email
        only username
    """

    response = client.resend_confirmation_code(
        ClientId=os.getenv('COGNITO_USER_CLIENT_ID'),
        Username=username
    )

    status = response['ResponseMetadata']['HTTPStatusCode']

    return status


def sign_in_auth(username: str, password: str, client: botocore.client.BaseClient = cognito_client):
    """
        sign in authentication -> returns user code in amazon user pool
    """

    response = client.initiate_auth(
        AuthFlow='USER_PASSWORD_AUTH',
        ClientId=os.getenv('COGNITO_USER_CLIENT_ID'),
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": password
        }
    )

    token = response['AuthenticationResult']['AccessToken']
    if not token:
        return None

    return token


def forgot_password_auth(username: str, client: botocore.client.BaseClient = cognito_client):
    """
        function that deals with a user's forgotten password, and sends an email prompt
    """
    response = client.forgot_password(
        ClientId=os.getenv('COGNITO_USER_CLIENT_ID'),
        Username=username
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']

    return status_code


def confirm_forgot_password_auth(username: str, code: str, new_password: str, client: botocore.client.BaseClient = cognito_client):
    """ 
        function that deals with a user's forgotten password, after receiving an email prompt and confirming the code, chooses a new password
    """
    response = client.confirm_forgot_password(
        ClientId=os.getenv('COGNITO_USER_CLIENT_ID'),
        Username=username,
        ConfirmationCode=code,
        Password=new_password
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']

    return status_code
