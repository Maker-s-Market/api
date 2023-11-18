from pydantic import BaseModel


class CreateRatingProduct(BaseModel):
    rating: float
    product_id: str


class UpdateRatingProduct(BaseModel):
    id: str
    rating: float
