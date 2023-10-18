from pydantic import BaseModel
from typing import List, Optional

from schemas.category import CategoryIdentifier


class CreateProduct(BaseModel):
    name: str
    description: str
    price: float
    stockable: bool
    stock: Optional[int]
    # image: str
    categories: List[CategoryIdentifier] = []
