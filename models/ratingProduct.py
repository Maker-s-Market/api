import datetime

from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import Session
from auth.auth import get_current_user
from db.database import Base, get_db
from fastapi import Depends, HTTPException
from repositories.productRepo import get_product_by_id
from repositories.userRepo import get_user

from schemas.rating import CreateRating, UpdateRating


def random_uuid():
    return str(uuid4())


class Rating(Base):
    __tablename__ = "rating product"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    rating = Column(Float, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(), nullable=False)

    user_id = Column(String(50), ForeignKey("user.id"))
    product_id = Column(String(50), ForeignKey("product.id"))

    def delete(self, db: Session = Depends(get_db)):
        db.delete(self)
        db.commit()
        return self

    def update(self, db: Session, rating_up: UpdateRating):
        self.rating = rating_up.rating
        self.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(self)
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id,
            "product_id": self.product_id
        }


def create_rating(rating: CreateRating, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username, db)
    if not get_product_by_id(rating.product_id, db=db):
        raise HTTPException(status_code=404, detail="Product not found")
    if rating.rating < 1 or rating.rating > 5:
        raise HTTPException(status_code=403, detail="Rating should be between 1 and 5")
    db_rating = Rating(**rating.model_dump())
    db_rating.user_id = user.id
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating
