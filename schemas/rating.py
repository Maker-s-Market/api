from pydantic import BaseModel

class CreateRating(BaseModel):
    rating: float
    product_id: str