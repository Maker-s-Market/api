import datetime

from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import Session
from auth.auth import get_current_user
from db.database import Base, get_db
from fastapi import Depends, HTTPException
from repositories.userRepo import get_user, get_user_by_id
from schemas.ratingSeller import UpdateRatingSeller, CreateRatingSeller


def random_uuid():
    return str(uuid4())


class RatingSeller(Base):
    __tablename__ = "rating seller"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    rating = Column(Float, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(), nullable=False)

    user_id = Column(String(50), ForeignKey("user.id"))
    seller_id = Column(String(50), ForeignKey("user.id"))

    def delete(self, db: Session = Depends(get_db)):
        db.delete(self)
        db.commit()
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id,
            "seller_id": self.seller_id
        }

    def update(self, db: Session, rating_up: UpdateRatingSeller):
        self.rating = rating_up.rating
        self.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(self)
        return self


def create_rating(rating: CreateRatingSeller, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username, db)
    if rating.seller_id == user.id:
        raise HTTPException(status_code=403, detail="You can not rate yourself")
    db_rating = RatingSeller(**rating.model_dump())
    db_rating.user_id = user.id
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating
