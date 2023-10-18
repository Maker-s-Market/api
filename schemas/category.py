from typing import Optional

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    id: int
    name: str
    slug: str
    icon: str
    numberViews: int
    created_at: Optional[float]
    updated_at: Optional[float]


class CreateCategory(BaseModel):
    name: str
    slug: str
    icon: str


class CategoryIdentifier(BaseModel):
    id: int


