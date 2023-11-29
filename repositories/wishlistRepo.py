from db.database import get_db
from models.wishList import Wishlist as WishlistModel

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException


def get_wishlist_user(user, db: Session = Depends(get_db)):
    wishlist_id = user.wishlist_id
    if wishlist_id is None:
        raise HTTPException(status_code=404, detail="Wishlist was not initialized")
    wishlist = db.query(WishlistModel).filter(WishlistModel.id == wishlist_id).first()
    if wishlist is None:
        raise HTTPException(status_code=404, detail="Wishlist not found for this user")

    return wishlist
