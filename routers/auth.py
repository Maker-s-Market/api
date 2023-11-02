import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from auth.JWTBearer import JWTBearer
from auth.auth import jwks, get_current_user
from auth.user_auth import check_email_auth, sign_up_auth, resend_email_code_auth, list_users, sign_in_auth, \
    forgot_password_auth, confirm_forgot_password_auth
from db.database import get_db
from models.user import User
from repositories.userRepo import new_user, delete_user, get_user
from schemas.user import CreateUser, ActivateUser, UserIdentifier, ChangePassword, UserLogin
from utils import verify_password

load_dotenv(".aws")

auth = JWTBearer(jwks)

router = APIRouter(tags=['Authentication and Authorization'])

client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION'))


@router.post("/auth/sign-up")
async def sign_up(user: CreateUser, db: Session = Depends(get_db)):
    if (db.query(User).filter(User.username == user.username).first() or
            db.query(User).filter(User.email == user.email).first()):
        raise HTTPException(status_code=500, detail="User already exists in database")

    if not verify_password(user.password):
        raise HTTPException(status_code=500, detail="Password does not meet requirements")

    new_user(user, db)
    try:
        status = sign_up_auth(user.username, user.email, user.password)
        if status != 200:
            delete_user(user.username, db)
            raise HTTPException(status_code=500, detail="Couldn't sign up")
        else:
            return JSONResponse(status_code=201, content=jsonable_encoder({"message": "User created"}))
    except client.exceptions.UsernameExistsException as e:
        delete_user(user.username, db)
        raise HTTPException(status_code=500, detail="User exists in cognito pool")
    except client.exceptions.InvalidPasswordException as e:
        delete_user(user.username, db)
        raise HTTPException(status_code=500, detail="Password is invalid!")
    except ClientError as e:
        delete_user(user.username, db)
        raise HTTPException(status_code=500, detail="Internal Server Error, try again later")


# TODO :simplificar erros
@router.post("/auth/verify-email")
async def verify_email(user: ActivateUser, db: Session = Depends(get_db)):
    try:
        status = check_email_auth(user.username, user.code)
        if status != 200:
            raise HTTPException(status_code=406, detail="Unable to confirm access, resend a code")
        else:
            user = get_user(user.username, db)
            user.active(db=db)
            return JSONResponse(status_code=200, content=jsonable_encoder({"message": "Email confirmed"}))
    except client.exceptions.TooManyFailedAttemptsException as e:
        raise HTTPException(status_code=406,
                            detail='Too many failed attempts at a code')
    except client.exceptions.ExpiredCodeException as e:
        raise HTTPException(status_code=406,
                            detail='Code expired, please resend a new code or check credentials')
    except client.exceptions.CodeMismatchException as e:
        raise HTTPException(status_code=406,
                            detail='Inserted code is not correct, please resend a new code or insert the correct one')
    except client.exceptions.UserNotFoundException as e:
        raise HTTPException(status_code=406,
                            detail='User was not found')
    except ClientError as e:
        raise HTTPException(status_code=500,
                            detail="Internal Server Error, try again later")


# TODO : NOT DONE and simplificar erros
@router.post("/auth/resend-email-code")
async def resend_email_code(user: UserIdentifier, db: Session = Depends(get_db)):
    # caso o utilizador nao exista na base de dados, nao faz sentido enviar o codigo
    print(list_users())

    try:
        status = resend_email_code_auth(user.identifier)
        if status != 200:
            raise HTTPException(status_code=406, detail="Couldn't send the code, try again later")
        else:
            return JSONResponse(status_code=status, content=jsonable_encoder({"message": "Code resent successfully"}))
    except client.exceptions.CodeDeliveryFailureException:
        raise HTTPException(status_code=400, detail="Couldn't send the code")
    except client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=400, detail="Username was not found in the pool")
    except ClientError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Server error")


@router.post("/auth/sign-in")
async def login(user: UserLogin):
    try:
        token = sign_in_auth(user.identifier, user.password)
        if token is None:
            raise HTTPException(status_code=404, detail="Error loging in...")
        else:
            return JSONResponse(status_code=200, content=jsonable_encoder({"token": token}))
    except client.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=406, detail="Wrong credentials, username/email or password incorrect.")
    except ClientError as e:
        raise HTTPException(status_code=500, detail="Server error")


# forgot password
@router.post("/auth/forgot-password")
async def forgot_password(user: UserIdentifier):
    try:
        status = forgot_password_auth(user.identifier)
        if status != 200:
            raise HTTPException(status_code=406, detail="Couldn't send the code, try again later")
        else:
            return JSONResponse(status_code=status, content=jsonable_encoder({"message": "Sent code to email"}))
    except client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=400, detail="Username was not found in the pool")
    except ClientError as e:
        raise HTTPException(status_code=500, detail="Server error")


@router.post("/auth/confirm-forgot-password")
async def confirm_forgot_password(user: ChangePassword):
    if verify_password(user.password) is False:
        raise HTTPException(status_code=500, detail="Password does not meet requirements")

    try:
        status = confirm_forgot_password_auth(username=user.identifier, code=user.code, new_password=user.password)
        if status != 200:
            raise HTTPException(status_code=406, detail="Couldn't confirm code")
        else:
            return JSONResponse(status_code=status,
                                content=jsonable_encoder({"message": "Password changed successfully"}))

    except client.exceptions.UserNotConfirmedException:
        raise HTTPException(status_code=400, detail="User was not confirmed")
    except client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=400, detail="User was not found in the user pool")
    except client.exceptions.CodeMismatchException:
        raise HTTPException(status_code=400, detail="Wrong code provided")
    except client.exceptions.ExpiredCodeException:
        raise HTTPException(status_code=400, detail="Code is expired or credentials are wrong")
    except client.exceptions.InvalidPasswordException:
        raise HTTPException(status_code=400, detail="Password is not acceptable")
    except ClientError as e:
        raise HTTPException(status_code=500, detail="Server error")


@router.get("/auth/current-user", dependencies=[Depends(auth)])
async def current_user(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return JSONResponse(status_code=200, content=jsonable_encoder(get_user(username=username, db=db).to_dict()))
