from pydantic import BaseModel


class CreateRatingSeller(BaseModel):
    rating: float
    seller_id: str


class UpdateRatingSeller(BaseModel):
    id: str  # id of SellerRating
    rating: float
