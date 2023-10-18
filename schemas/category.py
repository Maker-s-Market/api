from typing import Optional

from pydantic import BaseModel


class CreateCategory(BaseModel):
    name: str
    icon: str


class CategoryIdentifier(BaseModel):
    id: int


