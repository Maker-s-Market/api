from typing import Optional

from pydantic import BaseModel


class CategoryBase(BaseModel):
    id: int
    name: str
    slug: str
    icon: str
    numberViews: int = 0
    created_at: Optional[float]
    updated_at: Optional[float]

    class Config:
        orm_mode = True


class CreateCategory(BaseModel):
    name: str
    slug: str
    icon: str



