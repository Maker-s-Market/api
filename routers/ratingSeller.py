from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from auth.JWTBearer import JWTBearer
from db.database import get_db
from sqlalchemy.orm import Session
from auth.auth import get_current_user, jwks
from repositories.userRepo import get_user_by_id
from schemas.ratingSeller import CreateRatingSeller, UpdateRatingSeller
from repositories.ratingSellerRepo import rating_in_db, create_rating as cr

auth = JWTBearer(jwks)

router = APIRouter(tags=['Rating The Seller'])

@router.post("/rating-seller", dependencies=[Depends(auth)])
async def create_seller_rating(rating: CreateRatingSeller, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
    function that creates a rating for a certain seller
    TODO: test if functional
    """
    seller = get_user_by_id(rating.seller_id, db=db)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    if rating.rating < 0 or rating.rating > 5:
        return JSONResponse(status_code=403, content={"detail": "Rating should be between 0 and 5"})
    if rating_in_db(rating, db, username):
        return JSONResponse(status_code=403,
                            content={"detail": "A rating for this seller was already created, please edit it instead"})
    return JSONResponse(status_code=201,
                        content=jsonable_encoder(cr(rating=rating, db=db, username=username).to_dict()))

@router.put("/rating-seller", dependencies=[Depends(auth)])
async def put_seller_rating():
    pass