from pydantic import BaseModel

class CreateRating(BaseModel):
    rating: float
    product_id: str

class UpdateRating(BaseModel):
    id: str
    rating: float