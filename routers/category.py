from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db.database import get_db
from models.category import Category
from repositories.categoryRepo import new_category, get_all_categories, get_products_by_category, get_top_categories, \
    get_category_by_id
from schemas.category import CreateCategory

router = APIRouter(tags=['Category'])
MESSAGE_NOT_FOUND = "Category not found"


@router.post("/insert_data")
async def insert_data(db: Session = Depends(get_db)):
    category_id = str(uuid4())
    db.add(Category(id=category_id, name="category1", icon="icon1", slug="category1"))
    db.add(Category(id=str(uuid4()), name="category2", icon="icon2", slug="category2"))
    db.commit()
    return JSONResponse(status_code=201, content=jsonable_encoder({"message": "INSERT DATA SUCCESS"}))


@router.post("/category")
async def create_category(cat: CreateCategory, db: Session = Depends(get_db)):
    return JSONResponse(status_code=201, content=jsonable_encoder(new_category(db=db, cat=cat).to_dict()))


@router.put("/category/{category_id}")
async def update_category(category_id: str, cat: CreateCategory, db: Session = Depends(get_db)):
    category = get_category_by_id(db=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail=MESSAGE_NOT_FOUND)
    category.update_category(db=db, category=cat)
    return JSONResponse(status_code=200, content=jsonable_encoder(category.to_dict()))


@router.delete("/category/{category_id}")
async def delete_category(category_id: str, db: Session = Depends(get_db)):
    category = get_category_by_id(db=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail=MESSAGE_NOT_FOUND)
    category.delete_category(db=db)
    return JSONResponse(status_code=200, content=jsonable_encoder({"message": "DELETE DATA SUCCESS"}))


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    return JSONResponse(status_code=200, content=jsonable_encoder([category.to_dict()
                                                                   for category in get_all_categories(db=db)]))


@router.get("/category/{category_id}")
async def get_category(category_id: str, db: Session = Depends(get_db)):
    category = get_category_by_id(db=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail=MESSAGE_NOT_FOUND)
    products = get_products_by_category(db=db, category_id=category_id)
    category.increment_number_views(db=db)
    json_compatible_item_data = jsonable_encoder(category.to_dict())
    json_compatible_item_data['products'] = jsonable_encoder([product.to_dict_not_categories() for product in products])
    return JSONResponse(status_code=200, content=json_compatible_item_data)


@router.get("/top/category")
async def get_top_category(db: Session = Depends(get_db)):
    return JSONResponse(status_code=200, content=jsonable_encoder([category.to_dict()
                                                                   for category in get_top_categories(db=db)]))

