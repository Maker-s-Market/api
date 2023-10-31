from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from models.user import save_user, User as UserModel
from schemas.user import CreateUser


def new_user(user: CreateUser, db: Session = Depends(get_db)):
    return save_user(new_user=user, db=db)


def delete_user(username: str, db: Session = Depends(get_db)):
    return db.query(UserModel).filter(UserModel.username == username).first().delete(db=db)
