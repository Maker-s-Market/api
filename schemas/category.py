from pydantic import BaseModel


class CategoryBase(BaseModel):
    id: int
    name: str
    slug: str
    icon: str
    numberViews: int = 0
    created_at: float | None
    updated_at: float | None
    deleted_at: float | None

    class Config:
        orm_mode = True


class CreateCategory(BaseModel):
    name: str
    slug: str
    icon: str


