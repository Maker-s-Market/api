from boto3 import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from auth.auth import get_current_user
from db.database import get_db
from repositories.userRepo import get_user, get_seller_by_id, get_followers, get_user_by_id as user_by_id, get_follower_by_id
from schemas.user import UserUpdate
from auth.auth import get_current_user, jwks
from auth.JWTBearer import JWTBearer

router = APIRouter(tags=['User'])

auth = JWTBearer(jwks)

@router.put("/user")
async def update_user(update_user: UserUpdate, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
        Function that updates a user
    """
    user = get_user(username, db)
    if update_user.id != user.id:
        raise HTTPException(status_code=403, detail="You can only update your own user")
    else:
        user_updated = user.update(update_user, db)
        return JSONResponse(status_code=200, content=jsonable_encoder(user_updated.to_dict()))

@router.post("/user/follow-seller/{seller_id}", dependencies=[Depends(auth)])
async def follow_seller(seller_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
        follow (seller) 
        TODO: locally functional, need to do tests
    """
    user = get_user(username, db)
    if user.id == seller_id:
        raise HTTPException(status_code=403, detail="You can not follow yourself")  #working
    seller = get_seller_by_id(seller_id, db)
    if user.is_following(seller):
        raise HTTPException(status_code=403, detail="Already following this user/seller")
    user.follow(seller)
    user_updated = user.update(user, db)   #update user in db
    return JSONResponse(status_code=200, content = jsonable_encoder(user_updated.to_dict()))

@router.get("/user/follows")
async def get_users_i_follow(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
        check (seller) followers page   
        TODO: locally functional, need to do tests
    """
    followers = get_followers(username, db)
    return JSONResponse(status_code=200,
                        content=jsonable_encoder([follower.to_dict() for follower in followers]))

@router.delete("/user/remove-follower/{follower_id}")
async def remove_follower(follower_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """ 
        remove follower
        TODO: locally functional, need to do test
    """
    user = get_user(username, db)
    follower = get_follower_by_id(follower_id, db)

    if not user.is_following(follower):
        raise HTTPException(status_code=403, detail="You are not following this user")  #working
    
    user.unfollow(follower)
    user_updated = user.update(user, db)
    return JSONResponse(status_code=200, content = jsonable_encoder(user_updated.to_dict()))

@router.get("/user/followers/filter")
async def order_followerd_by(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """ filter followers page """
    
    pass

@router.get("/user/{user_id}")      #no need to be authenticated
async def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    """ 
        get user info (only some info) by user id
        #TODO: functional locally, need to do tests
    """
    user = user_by_id(user_id, db)
    return JSONResponse(status_code=200, content=jsonable_encoder(user.information()))
