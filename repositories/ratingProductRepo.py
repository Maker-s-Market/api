from fastapi import Depends, HTTPException
from auth.auth import get_current_user
from db.database import get_db
from schemas.rating import CreateRating, UpdateRating
from models.ratingProduct import create_rating as cr, Rating as RatingModel
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from repositories.userRepo import get_user


def create_rating(rating: CreateRating, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    return cr(rating=rating, db=db, username=username)


def in_db(rating: CreateRating, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username, db)
    rating_ = (db.query(RatingModel).filter(RatingModel.product_id == rating.product_id)
               .filter(RatingModel.user_id == user.id).first())
    if rating_:
        return True
    return False


def delete_rating(rating_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username=username, db=db)
    rating = db.query(RatingModel).filter(RatingModel.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found.")
    if rating.user_id != user.id:
        raise HTTPException(status_code=403,
                            detail="You are not the user who made this review. Only the owner of the review can delete it.")
    return rating


def update_rating(rating: UpdateRating, db: Session = Depends(get_db)):
    rating_ = db.query(RatingModel).filter(RatingModel.id == rating.id).first()
    return rating_.update(db=db, rating_up=rating_)


def get_ratings(product_id: str, db: Session = Depends(get_db)):
    return db.query(RatingModel).filter(RatingModel.product_id == product_id).all()


def get_rating_by_id(rating_id: str, db: Session = Depends(get_db)):
    return db.query(RatingModel).filter(RatingModel.id == rating_id).first()


def get_average(product_id: str, db: Session = Depends(get_db)):
    average = db.query(func.avg(RatingModel.rating).label('average')).filter(
        RatingModel.product_id == product_id).scalar()
    return "{:.1f}".format(average)
