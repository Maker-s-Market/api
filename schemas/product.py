from fastapi import UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional

from schemas.category import CategoryIdentifier


class CreateProduct(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0, description="The price must be greater than zero")
    stockable: bool
    stock: int
    discount: float
    # image: str #TODO image
    categories: List[CategoryIdentifier] = []
