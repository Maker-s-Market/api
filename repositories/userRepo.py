from fastapi import HTTPException

from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from models.user import save_user, User as UserModel, followers
from schemas.user import CreateUser


def new_user(user: CreateUser, db: Session = Depends(get_db)):
    return save_user(new_user=user, db=db)

def get_user_by_username(username: str, db: Session = Depends(get_db)):
    return db.query(UserModel).filter(UserModel.username == username).first()

def delete_user(username: str, db: Session = Depends(get_db)):
    return get_user_by_username(username, db).delete(db=db)

def get_user(username: str, db: Session = Depends(get_db)):
    db_user = get_user_by_username(username, db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

def get_seller(username: str, db: Session = Depends(get_db)):
    db_seller = get_user_by_username(username, db)
    if db_seller is None:
        raise HTTPException(status_code=404, detail="Seller not found")
    return db_seller

def get_followings(username:str, db:Session = Depends(get_db)):
    db_user = get_seller(username, db)
    followers = db_user.followers
    return followers

def get_user_by_id_query(id_user: str, db: Session = Depends(get_db)):
    return db.query(UserModel).filter(UserModel.id == id_user).first()

def get_user_by_id(id_user: str, db: Session = Depends(get_db)):
    db_user = get_user_by_id_query(id_user, db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

def get_following_by_id(id_user: str, db: Session = Depends(get_db)):
    db_user = get_user_by_id_query(id_user, db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Follower not found")
    return db_user

def get_followers(username: str, db: Session = Depends(get_db)):
    user = get_user(username, db)
    followers_list = (db.query(UserModel)
                    .join(followers, UserModel.id == followers.c.follower_id)
                    .filter(followers.c.followed_id == user.id)
                    .all())
    return followers_list

def get_seller_by_id(id_user: str, db: Session = Depends(get_db)):
    db_user = get_user_by_id_query(id_user, db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Seller not found")
    return db_user

def get_user_by_email(email: str, db: Session = Depends(get_db)):
    return db.query(UserModel).filter(UserModel.email == email).first()

