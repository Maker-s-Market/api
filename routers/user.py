from boto3 import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from auth.auth import get_current_user
from db.database import get_db
from repositories.productRepo import get_products_by_user_id
from repositories.userRepo import get_user, get_rated_user_by_id, get_followings, get_user_by_id as user_by_id, \
    get_followers, update_user_role
from schemas.user import UserUpdate
from auth.auth import get_current_user, jwks
from auth.JWTBearer import JWTBearer

router = APIRouter(tags=['User'])

auth = JWTBearer(jwks)


@router.put("/user")
async def update_user(update_user: UserUpdate, db: Session = Depends(get_db),
                      username: str = Depends(get_current_user)):
    """
        Function that updates a user
    """
    user = get_user(username, db)
    if update_user.id != user.id:
        raise HTTPException(status_code=403, detail="You can only update your own user")
    else:
        user_updated = user.update(update_user, db)
        return JSONResponse(status_code=200, content=jsonable_encoder(user_updated.information()))


@router.post("/user/follow-user/{rated_user_id}", dependencies=[Depends(auth)])
async def follow_user(rated_user_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
        follow (user) (Add to list of following)
    """
    user = get_user(username, db)
    if user.id == rated_user_id:
        raise HTTPException(status_code=403, detail="You can not follow yourself")  # working
    rated_user = get_rated_user_by_id(rated_user_id, db)
    if user.is_following(rated_user):
        raise HTTPException(status_code=403, detail="Already following this user")
    user.follow(rated_user)
    user_updated = user.update(user, db)  # update user in db
    return JSONResponse(status_code=200, content=jsonable_encoder(user_updated.information()))


@router.get("/user/following")
async def get_following(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
        check a user's following page
    """
    followers = get_followings(username, db)
    return JSONResponse(status_code=200,
                        content=jsonable_encoder([follower.information() for follower in followers]))


@router.delete("/user/remove-following/{following_id}")
async def remove_following(following_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """ 
        remove following
    """
    user = get_user(username, db)
    following = user_by_id(following_id, db)
    if following is None:
        raise HTTPException(status_code=404, detail="Follower not found")
    if not user.is_following(following):
        raise HTTPException(status_code=403, detail="You are not following this user")  # working

    user.unfollow(following)
    user_updated = user.update(user, db)
    return JSONResponse(status_code=200, content=jsonable_encoder(user_updated.information()))


@router.get("/user/followers")
async def order_followed_by(query_name: str = '', sort: str = '',
                            db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """ 
        filter followers page -> can filter by date joined/alphabetically/reviews
    """

    followers = get_followers(username=username, query=query_name, sort=sort, db=db)

    return JSONResponse(status_code=200, content=jsonable_encoder([follower.information() for follower in followers]))


@router.get("/user/{user_id}")
async def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    """ 
        get user info (only some info) by user id
    """
    user = user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    response = user.information()
    user.add_views(db=db)
    response["products"] = [product.to_dict() for product in get_products_by_user_id(user_id=response['id'], db=db)]
    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@router.put("/user/role/{role}", dependencies=[Depends(auth)])
async def change_user_role(role: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """ 
        change user role
    """
    if role != "Client" and role != "Premium":
        raise HTTPException(status_code=403, detail="User role is not valid. Valid options are: Client and Premium.")
    return JSONResponse(status_code=200, content=jsonable_encoder(update_user_role(role, username, db)))
