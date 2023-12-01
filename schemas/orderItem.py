from pydantic import BaseModel


class CreateOrderItem(BaseModel):
    product_id: str
    quantity: int
