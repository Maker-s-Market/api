from http.client import HTTPException
import os
import botocore
import boto3
from dotenv import load_dotenv


load_dotenv(".aws")

client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION'))


def sign_up(username: str, email: str, password: str):
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

def check_email_auth(username: str, code: str):
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

def resend_email_code(username: str):
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

def sign_in_auth(username: str, password: str):
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

    print(token)

    if not token:
        return None

    return token

def forgot_password(username: str):
    """ 
        function that deals with a user's forgotten password, and sends an email prompt
    """
    response = client.forgot_password(
        ClientId=os.getenv('COGNITO_USER_CLIENT_ID'),
        Username=username
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    print(str(status_code))

    return status_code

def confirm_forgot_password(username: str, code: str, new_password: str):
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


