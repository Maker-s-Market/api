import os

import json

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
import requests
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, RedirectResponse
from fastapi import Cookie

from auth.JWTBearer import JWTBearer
from auth.auth import jwks, get_current_user
from auth.user_auth import check_email_auth, sign_up_auth, resend_email_code_auth, sign_in_auth, \
    forgot_password_auth, confirm_forgot_password_auth
from db.database import get_db
from models.user import User
from repositories.orderRepo import get_orders_by_user_id
from repositories.productRepo import get_products_by_user_id
from repositories.userRepo import new_user, delete_user, get_user, get_user_by_email
from schemas.user import CreateUser, ActivateUser, UserIdentifier, ChangePassword, UserLogin, CreateUserIDP
from utils import verify_password

load_dotenv(".aws")

auth = JWTBearer(jwks)

router = APIRouter(tags=['Authentication and Authorization'])

client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION', 'us-east-1'))


@router.post("/auth/sign-up")
async def sign_up(user: CreateUser, db: Session = Depends(get_db)):
    """
        Function that puts a user in the AWS user pool and sends an email with a 1 time code
    """
    user.email = user.email.strip()
    user.username = user.username.strip()
    if (db.query(User).filter(User.username == user.username).first() or
            db.query(User).filter(User.email == user.email).first()):
        raise HTTPException(status_code=500, detail="User already exists in database")

    if not verify_password(user.password):
        raise HTTPException(status_code=500, detail="Password does not meet requirements")

    new_user(user, db)
    status = sign_up_auth(user.username, user.email, user.password)
    if status != 200:
        delete_user(user.username, db)
        raise HTTPException(status_code=500, detail="Couldn't sign up")
    else:
        return JSONResponse(status_code=201, content=jsonable_encoder({"message": "User created"}))


@router.post("/auth/verify-email")
async def verify_email(user: ActivateUser, db: Session = Depends(get_db)):
    """
        Function that checks if the code provided by email is correct or not
        If it is, the user is activated and can now sign in
    """
    user.username = user.username.strip()
    status = check_email_auth(user.username, user.code)
    if status != 200:
        raise HTTPException(status_code=406, detail="Unable to confirm access, resend a code")
    else:
        user = get_user(user.username, db)
        user.active(db=db)
        return JSONResponse(status_code=200, content=jsonable_encoder({"message": "Email confirmed"}))


@router.post("/auth/resend-email-code")
async def resend_email_code(user: UserIdentifier, db: Session = Depends(get_db)):
    """
        Resends the confirmation code to the specified email
    """
    user.identifier = user.identifier.strip()
    if get_user_by_email(user.identifier, db) is None:
        raise HTTPException(status_code=404, detail="User not found")

    status = resend_email_code_auth(user.identifier)
    if status != 200:
        raise HTTPException(status_code=406, detail="Couldn't send the code, try again later")
    else:
        return JSONResponse(status_code=status, content=jsonable_encoder({"message": "Code resent successfully"}))


@router.post("/auth/sign-in")
async def login(user: UserLogin):
    """
    Function that signs in a user and returns a token
    """
    user.identifier = user.identifier.strip()
    token = sign_in_auth(user.identifier, user.password)
    if token is None:
        raise HTTPException(status_code=404, detail="Error loging in...")
    else:
        return JSONResponse(status_code=200, content=jsonable_encoder({"token": token}))


# forgot password
@router.post("/auth/forgot-password")
async def forgot_password(user: UserIdentifier):
    """
        Function that sends a code to the user's email to change the password
    """
    user.identifier = user.identifier.strip()
    status = forgot_password_auth(user.identifier)
    if status != 200:
        raise HTTPException(status_code=406, detail="Couldn't send the code, try again later")
    else:
        return JSONResponse(status_code=status, content=jsonable_encoder({"message": "Sent code to email"}))


@router.post("/auth/confirm-forgot-password")
async def confirm_forgot_password(user: ChangePassword):
    """
    Function that changes the password of a user
    """
    user.identifier = user.identifier.strip()
    if verify_password(user.password) is False:
        raise HTTPException(status_code=500, detail="Password does not meet requirements")

    status = confirm_forgot_password_auth(username=user.identifier, code=user.code, new_password=user.password)
    if status != 200:
        raise HTTPException(status_code=406, detail="Couldn't change the password, try again later")
    else:
        return JSONResponse(status_code=status,
                            content=jsonable_encoder({"message": "Password changed successfully"}))


@router.get("/auth/me", dependencies=[Depends(auth)])
async def current_user(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Function that returns the current user
    """
    response = get_user(username=username, db=db).information()
    response['orders'] = [order.to_dict(db=db) for order in get_orders_by_user_id(user_id=response['id'], db=db)]
    response["products"] = [product.to_dict() for product in get_products_by_user_id(user_id=response['id'], db=db)]
    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@router.post("/auth/sign-up-idp")
async def sign_up_with_idp(user: CreateUserIDP, db: Session = Depends(get_db)):
    """
        Function that takes the call back IDP response code and returns the token
        TODO: add user to database if it doesn't exist, else return user in database (search for the username)
    """

    if (db.query(User).filter(User.username == user.username).first() or
            db.query(User).filter(User.email == user.email).first()):
        raise HTTPException(status_code=406, detail="User already exists in database")

    new_user(user, db)

    return JSONResponse(status_code=201, content=jsonable_encoder({"message": "User created"}))


@router.get("/auth/token_code")
async def get_token_from_code(code: str, db: Session = Depends(get_db)):
    """
    Function that takes the call back IDP response code and returns the token with user idp info
    """

    client_id = os.getenv("COGNITO_USER_CLIENT_ID")
    domain = "https://" + os.getenv("COGNITO_DOMAIN")
    redirect_url = os.getenv("MAKERS_URL_API") + "/auth/token_code"      # mudar isto depois se nao da erro de unauthorized client

    body = (
        'grant_type=authorization_code' +
        f'&client_id={client_id}' + f'&code={code}' +
        f'&redirect_uri={redirect_url}'
    )

    response = requests.post(
        f'{domain}/oauth2/token',
        body,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    response_body = json.loads(response.text)
    
    if "error" in response_body.keys():
        raise HTTPException(status_code=403, detail=("Error: " + response_body["error"]))

    access_token = response_body['access_token']

    user_info_response = requests.get(
        f'{domain}/oauth2/userInfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    user_info = json.loads(user_info_response.text)

    print(user_info)

    user_email = user_info["email"]
    username = user_info["username"]
    picture = None
    name = None
    if "picture" in user_info.keys():
        picture = user_info["picture"]
    if "name" in user_info.keys():
        name = user_info["name"]

    user = get_user_by_email(user_email, db)

    if user != None:
        response = RedirectResponse(url=(os.getenv("FRONTEND_SIGN_UP_IDP_LINK") + "?signType=signIn"), status_code=302)
        response.set_cookie(key="Authorization", value=access_token, secure=True, httponly=True)

        return response

    response = RedirectResponse(url=(os.getenv("FRONTEND_SIGN_UP_IDP_LINK") + "?signType=signUp"), status_code=302)
    
    response.set_cookie(key="email", value=user_email, secure=True, httponly=True)
    response.set_cookie(key="username", value=username, secure=True, httponly=True)
    response.set_cookie(key="picture", value=picture, secure=True, httponly=True)
    response.set_cookie(key="name", value=name, secure=True, httponly=True)
    response.set_cookie(key="Authorization", value=access_token, secure=True, httponly=True)

    return response

@router.get("/auth/token-read")
async def get_info_from_cookies(Authorization: str = Cookie(None), 
                                email: str = Cookie(None), 
                                name = Cookie(None), 
                                picture = Cookie(None), 
                                username = Cookie(None)):
    
    print("Authorization:", Authorization)
    print("email:", email)
    print("name:", name)
    print("picture:", picture)
    print("username:", username)
    
    info = {
        "Authorization:": Authorization,
        "email:": email,
        "name:": name,
        "picture:": picture,
        "username:": username
    }
    
    return JSONResponse(status_code=200, content=jsonable_encoder(info))