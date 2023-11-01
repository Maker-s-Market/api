import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import boto3

from botocore.client import ClientError

from auth.JWTBearer import JWTBearer
from auth.user_auth import sign_up, check_email_auth, resend_email_code as rc ,forgot_password as fp, confirm_forgot_password as cfp, sign_in_auth
from db.database import get_db
from models.user import User
from repositories.userRepo import new_user, delete_user, get_user
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


from schemas.user import CreateUser, UserIdentifier, UserLogin, ActivateUser, ChangePassword
from auth.auth import jwks
from dotenv import load_dotenv

load_dotenv(".aws")


auth = JWTBearer(jwks)

router = APIRouter(tags=['User'])

client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION'))


@router.get("/user/secure", dependencies=[Depends(auth)])
async def secure() -> bool:
    return True


@router.get("/user/not-secure")
async def not_secure() -> bool:
    return True


@router.post("/user/sign-up")
async def create_user(user: CreateUser, db: Session = Depends(get_db)):

    if (db.query(User).filter(User.username == user.username).first() or
            db.query(User).filter(User.email == user.email).first()):
        raise HTTPException(status_code=500, detail="User already exists in database")

    # TODO : CHANGE THIS TO A BETTER PASSWORD VALIDATION
    if len(user.password) < 8:
        raise HTTPException(status_code=500, detail="Password must have at least 8 characters")
    elif not any(char.isdigit() for char in user.password):
        raise HTTPException(status_code=500, detail="Password must have at least one digit")
    elif not any(char.isupper() for char in user.password):
        raise HTTPException(status_code=500, detail="Password must have at least one uppercase letter")
    elif not any(char.islower() for char in user.password):
        raise HTTPException(status_code=500, detail="Password must have at least one lowercase letter")
    elif not any(char in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '='] for char in user.password):
        raise HTTPException(status_code=500, detail="Password must have at least one special character")

    new_user(user, db)
    try:
        status = sign_up(user.username, user.email, user.password)
        # TODO : CHENGE TO A BETTER ERROR HANDLING
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
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error, try again later")

@router.post("/user/check_email")
async def check_email(user: ActivateUser, db: Session = Depends(get_db)):
    try:
        status = check_email_auth(user.username, user.code)
        # TODO : CHENGE TO A BETTER ERROR HANDLING
        if status != 200:
            raise HTTPException(status_code=406, detail="Unable to confirm access, resend a code")
        else:
            user = get_user(user.username, db)
            user.active(db=db)
            return JSONResponse(status_code=200, content=jsonable_encoder({"message": "Email confirmed"}))
    except client.exceptions.TooManyFailedAttemptsException as e:
        raise HTTPException(status_code=406, detail='Too many failed attemps at a code')
    except client.exceptions.ExpiredCodeException as e:
        raise HTTPException(status_code=406, detail='Code expired, please resend a new code or check credentials')
    except client.exceptions.CodeMismatchException as e:
        raise HTTPException(status_code=406, detail='Inserted code is not correct, please resend a new code or insert the correct one')
    except client.exceptions.UserNotFoundException as e:
        raise HTTPException(status_code=406, detail='User was not found')
    except ClientError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error, try again later")

@router.post("/user/login")
async def login(user: UserLogin):
    try:
        token = sign_in_auth(user.username, user.password)
        if token is None:
            raise HTTPException(status_code=404, detail="Error loging in...")
        else:
            return JSONResponse(status_code=200, content=jsonable_encoder({"token": token}))
    except client.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=406, detail="Wrong credentials, username/email or password incorrect.")
    except:
        raise HTTPException(status_code=500, detail="Server error")

@router.post("/user/resend_email_code")
async def resend_email_code(user: UserIdentifier):
    #accepts either email or username, but has 200 even if the email or username is incorrect, no exception to catch this
    try:
        status = rc(user.identifier)
        if status!=200:
            raise HTTPException(status_code=406, detail="Couldn't send the code, try again later")
        else:
            return JSONResponse(status_code=status, content=jsonable_encoder({"message":"Code resent successfully"}))
    except client.exceptions.CodeDeliveryFailureException:
        raise HTTPException(status_code=400, detail="Couldn't send the code")
    except client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=400, detail="Username was not found in the pool")
    except:
        raise HTTPException(status_code=500, detail="Server error")

@router.post("/user/forgot_password")
async def change_password(user: UserIdentifier):
    try:
        status = fp(user.identifier)
        if status!=200:
            raise HTTPException(status_code=406, detail="Couldn't send the code, try again later")
        else:
            return JSONResponse(status_code=status, content=jsonable_encoder({"message":"Sent code to email"}))
    except client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=400, detail="Username was not found in the pool")
    except:
        raise HTTPException(status_code=500, detail="Server error")

@router.post("/user/confirm_forgot_password")
async def confirm_forgot_password(user: ChangePassword):
    if len(user.password) < 8:
        raise HTTPException(status_code=500, detail="Password must have at least 8 characters")
    elif not any(char.isdigit() for char in user.password):
        raise HTTPException(status_code=500, detail="Password must have at least one digit")
    elif not any(char.isupper() for char in user.password):
        raise HTTPException(status_code=500, detail="Password must have at least one uppercase letter")
    elif not any(char.islower() for char in user.password):
        raise HTTPException(status_code=500, detail="Password must have at least one lowercase letter")
    elif not any(char in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '='] for char in user.password):
        raise HTTPException(status_code=500, detail="Password must have at least one special character")

    try: 
        status = cfp(username=user.identifier, code=user.code, new_password=user.password)
        if status!=200:
            raise HTTPException(status_code=406, detail="Couldn't confirm code")
        else:
            return JSONResponse(status_code=status, content=jsonable_encoder({"message":"Password changed successfully"}))
    
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
        print(e)
        raise HTTPException(status_code=500, detail="Server error")