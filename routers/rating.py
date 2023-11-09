from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from db.database import get_db
from schemas.rating import CreateRating
from auth.JWTBearer import JWTBearer
from auth.auth import get_current_user, jwks
from repositories.ratingRepo import create_rating as cr

auth = JWTBearer(jwks)

router = APIRouter(tags=['Rating'])

@router.post("/rating", dependencies=[Depends(auth)])
async def create_rating(rating: CreateRating, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
    function that creates a rating for a certain product
    """
    return JSONResponse(status_code=201,
                        content=jsonable_encoder(cr(rating=rating, db=db, username=username).to_dict()))
