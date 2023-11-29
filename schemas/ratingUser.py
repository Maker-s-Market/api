from pydantic import BaseModel


class CreateRatingUser(BaseModel):
    rating: float
    rated_user_id: str


class UpdateRatingUser(BaseModel):
    id: str  # id of rated user
    rating: float
