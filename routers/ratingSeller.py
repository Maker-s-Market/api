from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from auth.JWTBearer import JWTBearer
from db.database import get_db
from sqlalchemy.orm import Session
from auth.auth import get_current_user, jwks
from repositories.userRepo import get_seller_by_id, get_user, get_user_by_id
from schemas.ratingSeller import CreateRatingSeller, UpdateRatingSeller
from repositories.ratingSellerRepo import rating_in_db, create_rating as cr, get_rating, get_average as avg, \
    get_seller_rating_by_user as get_rating_by_seller_id_and_user, \
    get_seller_rating_by_rating_id, \
    get_ratings_by_seller_id

auth = JWTBearer(jwks)

router = APIRouter(tags=['Rating The Seller'])


@router.post("/rating-seller", dependencies=[Depends(auth)])
async def create_seller_rating(rating: CreateRatingSeller, db: Session = Depends(get_db),
                               username: str = Depends(get_current_user)):
    """
    function that creates a rating for a certain seller
    rate (seller) in catalog
    #TODO - functional locally, need to perform tests
    """
    seller = get_user_by_id(rating.seller_id, db=db)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    if rating.rating < 0 or rating.rating > 5:
        raise HTTPException(status_code=403, detail="Rating should be between 0 and 5")
    if rating_in_db(rating, db, username):
        raise HTTPException(status_code=403,
                            detail="A rating for this seller was already created, please edit it instead")
    rating = cr(rating=rating, db=db, username=username)
    seller.update_avg(db, float(avg(seller_id=rating.seller_id, db=db)))
    return JSONResponse(status_code=201,
                        content=jsonable_encoder(rating.to_dict()))


@router.put("/rating-seller", dependencies=[Depends(auth)])
async def put_seller_rating(rating: UpdateRatingSeller, db: Session = Depends(get_db),
                            username: str = Depends(get_current_user)):
    """
    endpoint that updates a seller rating
    edit seller rating
    #TODO - functional locally, need to perform tests
    """
    rating_ = get_rating(rating=rating, db=db)
    user = get_user(username, db)
    if rating_.user_id != user.id:
        raise HTTPException(status_code=403, detail="Only the user can alter their seller rating")
    if rating.rating > 5 or rating.rating < 1:
        raise HTTPException(status_code=403, detail="Rating should be between 0 and 5")

    rating_updated = rating_.update(db=db, rating_up=rating)
    seller = get_seller_by_id(rating_updated.seller_id, db)
    seller.update_avg(db, float(avg(seller_id=seller.id, db=db)))
    return JSONResponse(status_code=200, content=jsonable_encoder(rating_updated.to_dict()))


@router.delete("/rating-seller/{rating_id}", dependencies=[Depends(auth)])
async def delete_seller_rating(rating_id: str, db: Session = Depends(get_db),
                               username: str = Depends(get_current_user)):
    """
    endpoint that deletes a rating made to a seller
    #TODO: functional locally, need to perform tests
    """
    rating = get_seller_rating_by_rating_id(rating_id, db, username)
    seller = get_seller_by_id(rating.seller_id, db)
    rating.delete(db)
    seller.update_avg(db, float(avg(seller_id=rating.seller_id, db=db)))
    return JSONResponse(status_code=200, content={"detail": "Rating deleted successfully"})


@router.get("/rating-seller/{seller_id}", dependencies=[Depends(auth)])
async def get_my_seller_rating(seller_id: str, db: Session = Depends(get_db),
                               username: str = Depends(get_current_user)):
    """
        get my seller rating based on the seller_id
        #TODO: functional locally, need to perform tests
    """
    rating = get_rating_by_seller_id_and_user(seller_id, db, username)
    if not rating:
        return Response(status_code=204)
    return JSONResponse(status_code=200, content=jsonable_encoder(rating.to_dict()))


@router.get("/rating-seller/ratings/{seller_id}")
async def get_all_seller_rating(seller_id: str, db: Session = Depends(get_db)):
    """
        get my seller rating based on the seller_id
        #TODO: functional locally, need to perform tests
    """
    seller = get_seller_by_id(seller_id, db)
    return JSONResponse(status_code=200, content=jsonable_encoder([rating.to_dict()
                                                                   for rating in
                                                                   get_ratings_by_seller_id(seller_id, db)]))
