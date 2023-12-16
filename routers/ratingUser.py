from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from auth.JWTBearer import JWTBearer
from db.database import get_db
from sqlalchemy.orm import Session
from auth.auth import get_current_user, jwks
from repositories.userRepo import get_rated_user_by_id, get_user_by_id
from schemas.ratingUser import CreateRatingUser, UpdateRatingUser
from repositories.ratingUserRepo import rating_in_db, create_rating, get_average as avg, \
    get_rated_user_rating_by_user as get_rating_by_rated_user_id_and_user, \
    get_ratings_by_rated_user_id

auth = JWTBearer(jwks)

router = APIRouter(tags=['Rating The User'])


@router.post("/rating-user", dependencies=[Depends(auth)])
async def create_user_rating(rating: CreateRatingUser, db: Session = Depends(get_db),
                             username: str = Depends(get_current_user)):
    """
    function that creates a rating for a certain user
    rate (user) in catalog
    """
    rated_user = get_user_by_id(rating.rated_user_id, db=db)
    if not rated_user:
        raise HTTPException(status_code=404, detail="To be rated user not not found")
    if rating.rating < 0 or rating.rating > 5:
        raise HTTPException(status_code=403, detail="Rating should be between 0 and 5")
    if rating_in_db(rating, db, username):
        raise HTTPException(status_code=403,
                            detail="A rating for this user was already created, please edit it instead")
    rating = create_rating(rating=rating, db=db, username=username)
    rated_user.update_avg(db, float(avg(rated_user_id=rating.rated_user_id, db=db)))
    return JSONResponse(status_code=201,
                        content=jsonable_encoder(rating.to_dict()))


@router.put("/rating-user", dependencies=[Depends(auth)])
async def put_user_rating(upd_rating: UpdateRatingUser, db: Session = Depends(get_db),
                          username: str = Depends(get_current_user)):
    """
    endpoint that updates a rating made to a user
    edit user rating
    """
    rated_user = get_user_by_id(upd_rating.id, db=db)
    if not rated_user:
        raise HTTPException(status_code=404, detail="Rated user not found")
    rating = get_rating_by_rated_user_id_and_user(upd_rating.id, db, username)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if upd_rating.rating < 0 or upd_rating.rating > 5:
        raise HTTPException(status_code=403, detail="Rating should be between 0 and 5")
    rating.update(db, rating_up=upd_rating)
    rated_user.update_avg(db, float(avg(rated_user_id=rating.rated_user_id, db=db)))
    return JSONResponse(status_code=200, content=jsonable_encoder(rating.to_dict()))


@router.get("/rating-user/{rated_user_id}", dependencies=[Depends(auth)])
async def get_my_user_rating(rated_user_id: str, db: Session = Depends(get_db),
                             username: str = Depends(get_current_user)):
    """
        get my user rating based on the rated_user_id
    """
    rated_user = get_rated_user_by_id(rated_user_id, db)
    if not rated_user:
        raise HTTPException(status_code=404, detail="Rated user not found")
    rating = get_rating_by_rated_user_id_and_user(rated_user_id, db, username)
    if not rating:
        return Response(status_code=204)
    return JSONResponse(status_code=200, content=jsonable_encoder(rating.to_dict()))


@router.get("/rating-user/ratings/{rated_user_id}")
async def get_all_user_rating(rated_user_id: str, db: Session = Depends(get_db)):
    """
        get my user rating based on the rated_user_id
    """
    return JSONResponse(status_code=200, content=jsonable_encoder([rating.to_dict()
                                                                   for rating in
                                                                   get_ratings_by_rated_user_id(rated_user_id, db)]))
