from typing import List

from pydantic import BaseModel

from schemas.orderItem import CreateOrderItem


class CreateOrder(BaseModel):
    user_id: str
    total_price: float
    total_quantity: int
