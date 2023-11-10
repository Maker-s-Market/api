import os

import requests
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from auth.JWTBearer import JWKS, JWTBearer, JWTAuthorizationCredentials

load_dotenv(".aws")  # Automatically load environment variables from a '.env' file.

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
USER_POOL_ID = os.environ.get("USER_POOL_ID", "us-east-1_6cLcnDSn4")
jwks = JWKS.parse_obj(
    requests.get(
        f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"
    ).json()
)

auth = JWTBearer(jwks)


async def get_current_user(credentials: JWTAuthorizationCredentials = Depends(auth)) -> str:
    try:
        return credentials.claims["username"]
    except KeyError:
        HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Username missing")
