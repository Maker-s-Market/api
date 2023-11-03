from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from auth.JWTBearer import JWTBearer
from repositories.reviewRepo import create_review as cr, delete_review as dr, update_review as ur
from repositories.reviewRepo import get_review_by_id
from auth.auth import get_current_user, jwks

from db.database import get_db

from schemas.review import CreateReview, UpdateReview

router = APIRouter(tags=['Review'])

auth = JWTBearer(jwks)

@router.post("/review", dependencies=[Depends(auth)])
async def create_review(review: CreateReview, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    return JSONResponse(status_code=201, content=jsonable_encoder(cr(review=review, db=db, username=username).to_dict()))

@router.delete("/review", dependencies=[Depends(auth)])
async def delete_review(review_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    dr(review_id=review_id, db=db, username = username)
    return JSONResponse(status_code=200, content=jsonable_encoder({"message": "Review deleted succesfully"}))

@router.put("/review", dependencies=[Depends(auth)])
async def update_review(review: UpdateReview, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    review_db = ur(review=review, db=db, username=username)
    return JSONResponse(status_code=200, content=jsonable_encoder(review_db.to_dict()))
