from boto3 import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from db.database import get_db
from auth.auth import get_current_user, jwks
from auth.JWTBearer import JWTBearer
from repositories.productRepo import get_product_by_id
from repositories.userRepo import get_user
from repositories.wishlistRepo import get_wishlist_user

router = APIRouter(tags=['Wishlist'])

auth = JWTBearer(jwks)


@router.get("/wishlist", dependencies=[Depends(auth)])
async def get_user_wishlist(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """
        Function that gets the authenticated user's wishlist
    """
    user = get_user(username, db)
    wishlist_user = get_wishlist_user(user, db)

    return JSONResponse(status_code=200, content=jsonable_encoder(wishlist_user.to_dict()))


@router.post("/wishlist/{product_id}", dependencies=[Depends(auth)])
async def add_product_to_wishlist(product_id: str, db: Session = Depends(get_db),
                                  username: str = Depends(get_current_user)):
    """
        Function that adds a product to the authenticated user's wishlist
        #TODO: tested locally, needs code testing
    """
    user = get_user(username, db)
    wishlist_user = get_wishlist_user(user, db)
    product = get_product_by_id(product_id, db)
    if product is None:
        raise HTTPException(status_code=400, detail="Product not found")
    if product in wishlist_user.products:
        raise HTTPException(status_code=400, detail="Product already in wishlist")
    if product.user_id == user.id:
        raise HTTPException(status_code=400, detail="You can't add your own products to the wishlist")

    wishlist_updated = wishlist_user.add_product(db, product)

    return JSONResponse(status_code=200, content=jsonable_encoder(wishlist_updated.to_dict()))


@router.delete("/wishlist/{product_id}", dependencies=[Depends(auth)])
async def delete_product_from_wishlist(product_id: str, db: Session = Depends(get_db),
                                       username: str = Depends(get_current_user)):
    """
        Function that removes a product from the authenticated user's wishlist
        
    """
    user = get_user(username, db)
    wishlist_user = get_wishlist_user(user, db)
    product = get_product_by_id(product_id, db)
    if product is None:
        raise HTTPException(status_code=400, detail="Product not found")
    if product not in wishlist_user.products:
        raise HTTPException(status_code=400, detail="Product is not in your wishlist, nothing to remove")

    wishlist_user.remove_product(db, product)

    return JSONResponse(status_code=200, content={"detail": "Product deleted from wishlist successfully."})
