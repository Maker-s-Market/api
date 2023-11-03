from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from auth.JWTBearer import JWTBearer
from models.review import create_review as cr
from auth.auth import get_current_user, jwks

from db.database import get_db

from schemas.review import CreateReview

router = APIRouter(tags=['Review'])

auth = JWTBearer(jwks)

@router.post("/review", dependencies=[Depends(auth)])
async def create_review(review: CreateReview, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    return JSONResponse(status_code=201, content=jsonable_encoder(cr(review=review, db=db, username=username).to_dict()))
