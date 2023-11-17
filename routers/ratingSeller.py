from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from auth.JWTBearer import JWTBearer
from db.database import get_db
from sqlalchemy.orm import Session
from auth.auth import get_current_user, jwks
from repositories.userRepo import get_seller_by_id, get_user_by_id
from schemas.ratingSeller import CreateRatingSeller, UpdateRatingSeller
from repositories.ratingSellerRepo import rating_in_db, create_rating as cr, get_rating, get_average as avg

auth = JWTBearer(jwks)

router = APIRouter(tags=['Rating The Seller'])

@router.post("/rating-seller", dependencies=[Depends(auth)])
async def create_seller_rating(rating: CreateRatingSeller, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
    function that creates a rating for a certain seller
    rate (seller) in catalog
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
    rating = cr(rating=rating, db=db, username=username)
    seller.update_avg(db, float(avg(seller_id=rating.seller_id, db=db)))
    return JSONResponse(status_code=201,
                        content=jsonable_encoder(rating.to_dict()))

@router.put("/rating-seller", dependencies=[Depends(auth)])
async def put_seller_rating(rating: UpdateRatingSeller, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
    endpoint that updates a seller rating
    edit seller rating
    #TODO - test if functional
    """
    rating_ = get_rating(rating=rating, db=db)
    user = get_current_user(username)
    if rating_.user_id!=user.id:
        raise HTTPException(status_code=403, detail="Only the user can alter their seller rating")
    
    rating_updated = rating_.update(db=db, rating_up=rating)
    seller = get_seller_by_id(rating_updated.seller_id, db)
    seller.update_avg(db, float(avg(seller_id=rating.seller_id, db=db)))
    return JSONResponse(status_code=200, content=jsonable_encoder(rating_updated.to_dict()))

@router.delete("/rating-seller/{rating_id}", dependencies=[Depends(auth)])
async def delete_seller_rating(rating_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
    endpoint that deletes a rating made to a seller
    #TODO
    """
    pass


#TODO
# endpoint get rating de um seller 
#endpoints get all ratings made to sellers