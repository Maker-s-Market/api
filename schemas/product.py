from pydantic import Field
from pydantic import BaseModel
from typing import List, Optional

from schemas.category import CategoryBase, CategoryIdentifier


class ProductBase(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stockable: bool
    discount: Optional[float]
    number_views: Optional[int]

    created_at: Optional[float]
    updated_at: Optional[float]

    # image: str
    user_id: Optional[int]
    categories: list[CategoryBase]

    class Config:
        orm_mode = True


class CreateProduct(BaseModel):
    name: str
    description: str
    price: float
    stockable: bool
    stock: Optional[int]
    # image: str
    categories: list[CategoryIdentifier]
