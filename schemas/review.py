from pydantic import BaseModel


class CreateReview(BaseModel):
    text: str
    product_id: str

class UpdateReview(BaseModel):
    id: str
    text: str
    product_id: str