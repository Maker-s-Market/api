from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.JWTBearer import JWTBearer
from auth.user_auth import sign_up, check_email_auth, forgot_password, confirm_forgot_password, sign_in_auth
from db.database import get_db
from models.user import User
from repositories.userRepo import new_user, delete_user, get_user
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


from schemas.user import CreateUser, UserLogin, ActivateUser
from auth.auth import jwks, get_current_user


auth = JWTBearer(jwks)

router = APIRouter(tags=['User'])


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
        raise HTTPException(status_code=500, detail="User already exists")

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
    status = sign_up(user.username, user.email, user.password)
    # TODO : CHENGE TO A BETTER ERROR HANDLING
    if status != 200:
        delete_user(user.username, db)
        raise HTTPException(status_code=500, detail="Couldn't sign up")
    else:
        return JSONResponse(status_code=201, content=jsonable_encoder({"message": "User created"}))


@router.post("/user/check_email")
async def check_email(user: ActivateUser, db: Session = Depends(get_db)):
    status = check_email_auth(user.username, user.code)
    # TODO : CHENGE TO A BETTER ERROR HANDLING
    if status != 200:
        raise HTTPException(status_code=500, detail="Something is not right")
    else:
        user = get_user(user.username, db)
        user.active(db=db)
        return JSONResponse(status_code=200, content=jsonable_encoder({"message": "Email confirmed"}))


@router.post("/user/login")
async def login(user: UserLogin):
    token = sign_in_auth(user.username, user.password)
    print(user.password)
    if token is None:
        raise HTTPException(status_code=500, detail="Something is not right")

    else:
        return token
