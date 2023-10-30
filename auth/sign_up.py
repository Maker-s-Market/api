import os 
import boto3
from dotenv import load_dotenv
load_dotenv(".aws")


client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION'))

def sign_up(username: str, email: str, password: str, name: str, picture: str, city: str, region: str, role: int):
    """
        function that puts a user in the AWS user pool and sends an email with a 1 time code 
    """
    response =client.sign_up(
        ClientId=os.getenv('COGNITO_USER_CLIENT_ID'),
        Username=username,
        Password=password,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': email,
            },
            {
                'Name': 'name',
                'Value': name,
            },
            {
                'Name': 'region',
                'Value': region,
            },            
            {
                'Name': 'city',
                'Value': city,
            },
            {
                'Name': 'picture',
                'Value': picture,
            },
            {
                'Name': 'role',
                'Value': role,
            },

        ]
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    print(str(status_code))

    return status_code


def check_email(username: str, code: str):
    """
        function that checks if the code provided by email is correct or not
    """
    response = client.confirm_sign_up(
        ClientId=os.getenv('COGNITO_USER_CLIENT_ID'),
        Username=username,
        ConfirmationCode=code
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    print(str(status_code))

    return status_code


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
        Confirmation_Code=code,
        Password=new_password
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    print(str(status_code))

    return status_code


def sign_in():
    response = client.initiate_auth(
        ClientId=os.get
    )
    
    pass
