from boto3 import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from auth.auth import get_current_user
from db.database import get_db
from repositories.userRepo import get_user
from schemas.user import UserUpdate

router = APIRouter(tags=['User'])


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



