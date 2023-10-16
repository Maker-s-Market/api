from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db.database import get_db
from repositories.categoryRepo import new_category, get_all_categories, get_products_by_category, get_top_categories
from schemas.category import CreateCategory

router = APIRouter(tags=['Category'])


@router.post("/category")
async def create_category(cat: CreateCategory, db: Session = Depends(get_db)):
    return new_category(db=db, cat=cat)


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    return get_all_categories(db=db)


@router.put("/category/{category_id}")
async def get_category(category_id: int, db: Session = Depends(get_db)):
    # return list the products of the category
    return get_products_by_category(db=db, category_id=category_id)


@router.get("/top/category")
async def get_top_category(db: Session = Depends(get_db)):
    return get_top_categories(db=db)
