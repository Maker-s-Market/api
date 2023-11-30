from typing import List

from pydantic import BaseModel, Field

from schemas.category import CategoryIdentifier

class CreateOrderItem(BaseModel):
    product_id: str
    quantity: int