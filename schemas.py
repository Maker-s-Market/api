import uuid

from pydantic import BaseModel
from typing import List, Optional


class Category(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    created_at: float | None
    updated_at: float | None
    products: List[str] = []


class CreateCategory(BaseModel):
    name: str
    slug: str
    description: str


class Product(BaseModel):
    id: int
    name: str
    description: str
    created_at: float
    updated_at: float
    price: float
    stockable: bool
    stock: int
    discount: float
    image: str
    category: str

class CreateProduct(BaseModel):
    name: str
    description: str
    price: float
    stockable: bool
    stock: int
    discount: float
    image: str
    category: str

class Review(BaseModel):
    id: int
    created_at: float
    updated_at: float
    comment: str

class CreateReview(BaseModel):
    comment: str

class Rating(BaseModel):
    id: int
    created_at: float
    updated_at: float
    rating: float

class CreateRating(BaseModel):
    rating: float

class WishList(BaseModel):
    id: int
    created_at: float
    updated_at: float

#classe createwishlist?

class ShoppingCart(BaseModel):
    id: int
    created_at: float
    updated_at: float

#classe createshoppingcart?

class Order(BaseModel):
    id: int
    created_at: float
    updated_at: float
    status: int

class CreateOrder(BaseModel):
    status: int

class OrderLine(BaseModel):
    id: int
    created_at: float
    updated_at: float
    amount: float
    line_price: float
    status: int

class CreateOrderLine(BaseModel):
    amount: float
    line_price: float
    status: int