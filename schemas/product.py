from typing import List

from pydantic import BaseModel, Field

from schemas.category import CategoryIdentifier


class CreateProduct(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0, description="The price must be greater than zero")
    stockable: bool
    stock: int
    discount: float
    image: str
    categories: List[CategoryIdentifier] = []

class UpdateDiscount(BaseModel):
    product_id: str
    discount: float
