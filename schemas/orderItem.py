from pydantic import BaseModel


class CreateOrderItem(BaseModel):
    product_id: str
    quantity: int


class CreateOrderItemOrderId(BaseModel):
    order_id: str
    product_id: str
    quantity: int
