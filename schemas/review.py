from pydantic import BaseModel


class CreateReview(BaseModel):
    text: str
    product_id: str

class CreateReviewId(BaseModel):
    text: str
    user_id: str
    product_id: str