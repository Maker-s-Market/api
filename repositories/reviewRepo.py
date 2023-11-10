from fastapi import Depends
from sqlalchemy.orm import Session
from auth.auth import get_current_user

from db.database import get_db
from models.review import Review as ReviewModel, create_review as cr
from repositories.userRepo import get_user
from schemas.review import CreateReview, UpdateReview


def get_review_by_id(review_id: str, db: Session = Depends(get_db)):
    return db.query(ReviewModel).filter(ReviewModel.id == review_id).first()


def create_review(review: CreateReview, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    return cr(review=review, db=db, username=username)


def update_review(review: UpdateReview, review_db: ReviewModel, db: Session = Depends(get_db)):
    return review_db.update_review(db=db, review=review)


def get_reviews(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username=username, db=db)
    return db.query(ReviewModel).filter(ReviewModel.user_id == user.id)


def get_product_reviews(product_id, db: Session = Depends(get_db)):
    return db.query(ReviewModel).filter(ReviewModel.product_id == product_id)
