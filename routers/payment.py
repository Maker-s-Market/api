import os

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from auth.JWTBearer import JWTBearer
from auth.auth import jwks

env_path = os.path.join(os.path.dirname(__file__), "..", '.env')
load_dotenv(env_path)
stripe.api_key = os.getenv("STRIPE_KEY")

auth = JWTBearer(jwks)

router = APIRouter(tags=['Payment'])


@router.post("/process-payment", dependencies=[Depends(auth)])
async def payment(amount: float):
    amount_in_cents = int(amount * 100)
    if amount_in_cents < 50:
        detail = "Amount must be greater than 50 cents."
        raise HTTPException(status_code=400, detail=detail)

    payment = stripe.PaymentIntent.create(
        amount=amount_in_cents,
        currency="eur",
        payment_method_types=["card"],
        description="Order payment in MarkersMarket",
    )
    return JSONResponse(status_code=201,
                        content=jsonable_encoder({"client_secret": payment.client_secret}))
