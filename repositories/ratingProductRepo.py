from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from auth.auth import get_current_user
from db.database import get_db
from models.ratingProduct import create_rating as cr, RatingProduct as RatingModel
from repositories.userRepo import get_user
from repositories.productRepo import get_products_by_user_id
from schemas.ratingProduct import CreateRatingProduct as CreateRating, UpdateRatingProduct as UpdateRating


def create_rating(rating: CreateRating, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    return cr(rating=rating, db=db, username=username)


def in_db(rating: CreateRating, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username, db)
    rating_ = (db.query(RatingModel).filter(RatingModel.product_id == rating.product_id)
               .filter(RatingModel.user_id == user.id).first())
    if rating_:
        return True
    return False


def update_rating(update_rating: UpdateRating, db: Session = Depends(get_db)):
    rating = db.query(RatingModel).filter(RatingModel.product_id == update_rating.id).first()
    return rating.update(db=db, rating_up=update_rating)


def get_average(product_id: str, db: Session = Depends(get_db)):
    average = db.query(func.avg(RatingModel.rating).label('average')).filter(
        RatingModel.product_id == product_id).scalar()
    if average is None:
        average = 0.0
    return "{:.1f}".format(average)


def get_rating_by_product_and_user(product_id: str, username: str, db: Session = Depends(get_db)):
    user = get_user(username, db)
    return (db.query(RatingModel).filter(RatingModel.product_id == product_id)
            .filter(RatingModel.user_id == user.id).first())

def get_ratings_by_product_id(product_id: str, db: Session = Depends(get_db)):
    return (db.query(RatingModel).filter(RatingModel.product_id == product_id)).all()
