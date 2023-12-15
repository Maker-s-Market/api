import os

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from auth.JWTBearer import JWTBearer
from auth.auth import jwks, get_current_user
from db.database import get_db
from repositories.userRepo import get_user
from routers.orders import send_email

env_path = os.path.join(os.path.dirname(__file__), "..", '.env')
load_dotenv(env_path)
stripe.api_key = os.getenv("STRIPE_KEY")

auth = JWTBearer(jwks)

router = APIRouter(tags=['Payment'])


@router.post("/payment/process-payment", dependencies=[Depends(auth)])
async def payment(amount: float, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    amount_in_cents = int(amount * 100)
    user = get_user(username, db)
    if amount_in_cents < 50:
        detail = "Amount must be greater than 50 cents."
        raise HTTPException(status_code=400, detail=detail)

    payment = stripe.PaymentIntent.create(
        amount=amount_in_cents,
        currency="eur",
        payment_method_types=["card"],
        description="Payment in MarkersMarket",
    )

    await send_email(user.email, "Payment processed successfully!")

    return JSONResponse(status_code=201,
                        content=jsonable_encoder({"client_secret": payment.client_secret}))
