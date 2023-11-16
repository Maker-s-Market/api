from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Response
from db.database import get_db
from repositories.productRepo import get_product_by_id
from repositories.userRepo import get_user
from schemas.ratingProduct import CreateRatingProduct as CreateRating, UpdateRatingProduct as UpdateRating
from auth.JWTBearer import JWTBearer
from auth.auth import get_current_user, jwks
from repositories.ratingProductRepo import (create_rating as cr, delete_rating as dr, update_rating as update,
                                            get_ratings, get_average as avg, in_db as rating_in_db, get_rating_by_id,
                                            get_rating_by_product_and_user)

auth = JWTBearer(jwks)

router = APIRouter(tags=['Rating The Product'])

@router.post("/rating-product", dependencies=[Depends(auth)])
async def create_rating(rating: CreateRating, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
    function that creates a rating for a certain product
    """
    product = get_product_by_id(rating.product_id, db=db)
    if get_product_by_id(rating.product_id, db=db) is None:
        return JSONResponse(status_code=404, content={"detail": "Product not found"})
    if rating.rating < 1 or rating.rating > 5:
        return JSONResponse(status_code=403, content={"detail": "Rating should be between 1 and 5"})
    if rating_in_db(rating, db, username):
        return JSONResponse(status_code=403,
                            content={"detail": "A rating for this product was already created, please edit it instead"})
    rating = cr(rating=rating, db=db, username=username)
    product.update_avg(db, float(avg(product_id=rating.product_id, db=db)))
    return JSONResponse(status_code=201,
                        content=jsonable_encoder(rating.to_dict()))


@router.put("/rating-product", dependencies=[Depends(auth)])
async def update_rating(upd_rating: UpdateRating, db: Session = Depends(get_db),
                        username: str = Depends(get_current_user)):
    """
    Update an existing rating
    """
    if upd_rating.rating < 1 or upd_rating.rating > 5:
        return JSONResponse(status_code=403, content={"detail": "Rating should be between 1 and 5"})
    rating = get_rating_by_id(upd_rating.id, db=db)
    if rating is None:
        return JSONResponse(status_code=404, content={"detail": "Rating not found"})
    if rating.user_id != get_user(username, db).id:
        return JSONResponse(status_code=403,
                            content={"detail": "You are not the user who made this review. "
                                               "Only the owner of the review can delete it."})
    updated = update(update_rating=upd_rating, db=db)
    product = get_product_by_id(rating.product_id, db=db)
    product.update_avg(db, float(avg(product_id=rating.product_id, db=db)))
    return JSONResponse(status_code=200,
                        content=jsonable_encoder(updated.to_dict()))


@router.get("/rating-product/{product_id}", dependencies=[Depends(auth)])
async def get_rating(product_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
    Get review the user made for a certain product
    """
    if get_product_by_id(product_id, db=db) is None:
        return JSONResponse(status_code=404, content={"detail": "Product not found"})
    rating = get_rating_by_product_and_user(product_id=product_id, username=username, db=db)
    if rating is None:
        return Response(status_code=204)
    return JSONResponse(status_code=200, content=jsonable_encoder(rating.to_dict()))


# TODO: check if functional
@router.get("/rating-product/ratings/{product_id}")
async def get_ratings_product(product_id: str, db: Session = Depends(get_db)):
    """
    Get a product's ratings
    """
    if get_product_by_id(product_id, db=db) is None:
        return JSONResponse(status_code=404, content={"detail": "Product not found"})
    return JSONResponse(status_code=200, content=jsonable_encoder([rating.to_dict()
                                                                   for rating in
                                                                   get_ratings(product_id=product_id, db=db)]))

# TODO: check if functional
@router.delete("/rating-product/{rating_id}", dependencies=[Depends(auth)])
async def delete_rating(rating_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
    Delete an existing rating
    """
    return JSONResponse(status_code=200,
                        content=jsonable_encoder(dr(rating_id=rating_id, db=db, username=username).to_dict()))

