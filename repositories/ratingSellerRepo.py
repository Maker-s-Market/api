from fastapi import Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from auth.auth import get_current_user
from db.database import get_db
from repositories.userRepo import get_seller_by_id, get_user
from models.ratingSeller import RatingSeller as RatingModel, create_rating as cr
from schemas.ratingSeller import CreateRatingSeller, UpdateRatingSeller


def rating_in_db(rating: CreateRatingSeller, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username, db)
    rating_ = (db.query(RatingModel).filter(RatingModel.seller_id == rating.seller_id)
               .filter(RatingModel.user_id == user.id).first())
    if rating_:
        return True
    return False


def create_rating(rating: CreateRatingSeller, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    return cr(rating=rating, db=db, username=username)


def get_rating(rating: UpdateRatingSeller, db: Session = Depends(get_db)):
    rating_ = db.query(RatingModel).filter(RatingModel.id == rating.id).first()
    if rating_ == None:
        raise HTTPException(status_code=404, detail="Rating was not found")
    return rating_


def get_average(seller_id: str, db: Session = Depends(get_db)):
    average = db.query(func.avg(RatingModel.rating).label('average')).filter(
        RatingModel.seller_id == seller_id).scalar()
    if average is None:
        average = 0.0
    return "{:.1f}".format(average)


def get_seller_rating_by_user(seller_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username, db)
    rating = db.query(RatingModel).filter(RatingModel.seller_id == seller_id).filter(
        RatingModel.user_id == user.id).first()
    return rating


def get_ratings_by_seller_id(seller_id: str, db: Session = Depends(get_db)):
    ratings = db.query(RatingModel).filter(RatingModel.seller_id == seller_id).all()
    return ratings
