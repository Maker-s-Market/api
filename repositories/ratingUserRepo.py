from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from auth.auth import get_current_user
from db.database import get_db
from repositories.userRepo import get_user
from models.ratingUser import RatingUser as RatingModel, create_rating as cr
from schemas.ratingUser import CreateRatingUser


def rating_in_db(rating: CreateRatingUser, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username, db)
    rating_ = (db.query(RatingModel).filter(RatingModel.rated_user_id == rating.rated_user_id)
               .filter(RatingModel.user_id == user.id).first())
    if rating_:
        return True
    return False


def create_rating(rating: CreateRatingUser, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    return cr(rating=rating, db=db, username=username)


def get_average(rated_user_id: str, db: Session = Depends(get_db)):
    average = db.query(func.avg(RatingModel.rating).label('average')).filter(
        RatingModel.rated_user_id == rated_user_id).scalar()
    if average is None:
        average = 0.0
    return "{:.1f}".format(average)


def get_rated_user_rating_by_user(user_rated_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username, db)
    rating = db.query(RatingModel).filter(RatingModel.rated_user_id == user_rated_id).filter(
        RatingModel.user_id == user.id).first()
    return rating


def get_ratings_by_rated_user_id(user_rated_id: str, db: Session = Depends(get_db)):
    ratings = db.query(RatingModel).filter(RatingModel.rated_user_id == user_rated_id).all()
    return ratings
