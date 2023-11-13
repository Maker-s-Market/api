from fastapi import HTTPException

from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from models.user import save_user, User as UserModel
from schemas.user import CreateUser


def new_user(user: CreateUser, db: Session = Depends(get_db)):
    return save_user(new_user=user, db=db)


def delete_user(username: str, db: Session = Depends(get_db)):
    return db.query(UserModel).filter(UserModel.username == username).first().delete(db=db)


def get_user(username: str, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

def get_seller(username: str, db: Session = Depends(get_db)):
    db_seller = db.query(UserModel).filter(UserModel.username == username).first()
    if db_seller is None:
        raise HTTPException(status_code=404, detail="Seller not found")
    return db_seller

def get_user_by_id(id_user: str, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == id_user).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

def get_seller_by_id(id_user: str, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == id_user).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Seller not found")
    return db_user

def get_user_by_email(email: str, db: Session = Depends(get_db)):
    return db.query(UserModel).filter(UserModel.email == email).first()

