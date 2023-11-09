from fastapi import Depends, HTTPException
from auth.auth import get_current_user
from db.database import get_db
from schemas.rating import CreateRating
from models.rating import create_rating as cr, Rating as RatingModel
from sqlalchemy.orm import Session
from repositories.userRepo import get_user

def create_rating(rating: CreateRating, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    if in_db(rating, db, username):
        raise HTTPException(status_code = 403, detail="A rating for this product was already created, please edit it instead")
    return cr(rating=rating, db=db, username=username)

def in_db(rating: CreateRating, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username, db)
    rating_ = db.query(RatingModel).filter(RatingModel.product_id==rating.product_id).filter(RatingModel.user_id==user.id).first()
    if rating_:
        return True
    return False

