from fastapi import APIRouter, Depends, HTTPException
from auth.JWTBearer import JWTBearer
from auth.user_auth import sign_up, check_email_auth, forgot_password, confirm_forgot_password, sign_in_auth

from schemas.user import CreateUser, UserLogin
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
async def create_user(user: CreateUser):
    status = sign_up(user.username, user.email, user.password)

    if status != 200:
        raise HTTPException(status_code=500, detail="Couldn't sign up")
    
    else:
        #colocar na db
        pass

    pass

@router.get("/user/check_email")
async def check_email(username: str, code: str):
    status = check_email_auth(username, code)
    if status != 200:
        raise HTTPException(status_code=500, detail="Code is not correct")
    
    else:
        #colocar na db
        pass
    pass

@router.post("/user/login")
async def login(user: UserLogin):
    token = sign_in_auth(user.username, user.password)
    print(user.password)
    if token is None:
        raise HTTPException(status_code=500, detail="Something is not right")
    
    else:
        return token