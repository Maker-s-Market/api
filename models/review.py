import datetime
from uuid import uuid4

from fastapi import Depends
from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.orm import Session

from auth.auth import get_current_user
from db.database import get_db, Base
from repositories.userRepo import get_user, get_user_by_id
from schemas.review import CreateReview, UpdateReview


def random_uuid():
    return str(uuid4())


class Review(Base):
    __tablename__ = "review"

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    text = Column(String(1000), index=True, nullable=False, default="")

    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(), nullable=False)

    user_id = Column(String(50), ForeignKey("user.id"))
    product_id = Column(String(50), ForeignKey("product.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id,
            "product_id": self.product_id
        }
    
    def to_dict_user(self, db):
        return {
            "id": self.id,
            "text": self.text,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user": get_user_by_id(self.user_id, db).information()
        }

    def delete(self, db: Session = Depends(get_db)):
        db.delete(self)
        db.commit()
        return self

    def update_review(self, db: Session, review: UpdateReview):
        self.text = review.text
        self.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(self)
        return self


def create_review(review: CreateReview, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    user = get_user(username, db)
    db_review = Review(**review.model_dump())
    db_review.user_id = user.id
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review
