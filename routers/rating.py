from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from db.database import get_db
from repositories.productRepo import get_product_by_id
from repositories.userRepo import get_user
from schemas.rating import CreateRating, UpdateRating
from auth.JWTBearer import JWTBearer
from auth.auth import get_current_user, jwks
from repositories.ratingRepo import create_rating as cr, delete_rating as dr, update_rating as ur, get_ratings as gr, \
    get_average as ga, in_db as rating_in_db

auth = JWTBearer(jwks)

router = APIRouter(tags=['Rating'])


@router.post("/rating", dependencies=[Depends(auth)])
async def create_rating(rating: CreateRating, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
    function that creates a rating for a certain product
    """
    if get_product_by_id(rating.product_id, db=db) is None:
        return JSONResponse(status_code=404, content={"detail": "Product not found"})
    if rating.rating < 1 or rating.rating > 5:
        return JSONResponse(status_code=403, content={"detail": "Rating should be between 1 and 5"})
    if rating_in_db(rating, db, username):
        return JSONResponse(status_code=403,
                            content={"detail": "A rating for this product was already created, please edit it instead"})
    return JSONResponse(status_code=201,
                        content=jsonable_encoder(cr(rating=rating, db=db, username=username).to_dict()))


# TODO: check if functional
@router.delete("/rating/{rating_id}", dependencies=[Depends(auth)])
async def delete_rating(rating_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
    Delete an existing rating
    """
    return JSONResponse(status_code=200,
                        content=jsonable_encoder(dr(rating_id=rating_id, db=db, username=username).to_dict()))


# TODO: check if functional
@router.put("/rating", dependencies=[Depends(auth)])
async def update_rating(upd_rating: UpdateRating, db: Session = Depends(get_db),
                        username: str = Depends(get_current_user)):
    """
    Update an existing rating
    """
    return JSONResponse(status_code=200,
                        content=jsonable_encoder(ur(rating=upd_rating, db=db, username=username).to_dict()))


# TODO: check if functional
@router.get("/rating/{product_id}")
async def get_ratings_product(product_id: str, db: Session = Depends(get_db)):
    """
    Get all product's rating
    """
    return JSONResponse(status_code=200, content=jsonable_encoder([rating.to_dict()
                                                                   for rating in gr(product_id=product_id, db=db)]))


# TODO: check if functional
@router.get("/rating/avg/{product_id}")
async def get_average_rating_product(product_id: str, db: Session = Depends(get_db)):
    """
    Get average rating from a product
    """
    return JSONResponse(status_code=200, content={"average": str(ga(product_id=product_id, db=db))})
    pass
