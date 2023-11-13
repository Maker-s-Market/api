from fastapi import APIRouter, Depends
from auth.auth import get_current_user, jwks
from auth.JWTBearer import JWTBearer
from boto3 import Session
from db.database import get_db
from repositories.userRepo import get_seller, get_user_by_id


router = APIRouter(tags=['Seller'])

auth = JWTBearer(jwks)

@router.get("/seller/followers/{seller_id}", dependencies=[Depends(auth)])
async def get_seller_followers(seller_id: str, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    seller = get_user_by_id(seller_id, db)
    print(seller.followed)
    #TODO: complete
    pass
