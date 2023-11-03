from fastapi import HTTPException

from fastapi import Depends
from sqlalchemy.orm import Session
from auth.auth import get_current_user

from db.database import get_db
from models.review import Review as ReviewModel, create_review as cr
from repositories.userRepo import get_user
from schemas.review import CreateReview, UpdateReview

def get_review_by_id(review_id: str, db: Session = Depends(get_db)):
    return db.query(ReviewModel).filter(ReviewModel.id == review_id).first()

def delete_review(review_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    review = get_review_by_id(review_id=review_id, db=db)
    if not review:
        raise HTTPException(status_code=404, detail="No review found with that id")
    user = get_user(username, db)
    if user.id != review.user_id:
        raise HTTPException(status_code=403, detail="Only the user can change its reviews")
    if not review: 
        raise HTTPException(status_code=404, detail = "Review not found")
    return db.query(ReviewModel).filter(ReviewModel.id == review_id).first().delete(db=db)


def create_review(review: CreateReview, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    return cr(review=review, db=db, username=username)

def update_review(review: UpdateReview, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    review_ = get_review_by_id(review.id, db=db)
    user = get_user(username, db)
    if user.id != review_.user_id:
        raise HTTPException(status_code=403, detail="Only the user can update its reviews")
    return review_.update_review(db=db, review=review)
    

def get_reviews():
    pass