import os
from contextlib import asynccontextmanager
from uuid import uuid4

import boto3
from fastapi import FastAPI, Depends, Request, UploadFile, File
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db.create_database import create_tables
from db.database import get_db, SessionLocal
from models.category import Category
from models.product import Product
from routers import product, category


@asynccontextmanager
async def lifespan(app):
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(category.router)
app.include_router(product.router)

# Configure AWS credentials
s3 = boto3.client(
    's3',
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    response = await call_next(request)
    request.state.db.close()
    return response


@app.get("/")
async def root():
    return {"message": "hello World!"}


@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    # Generate a unique filename for the uploaded file
    filename = file.filename

    # Upload the file to the S3 bucket
    s3.upload_fileobj(file.file, os.getenv("BUCKET_NAME"), filename)

    # Generate a pre-signed URL to access the image in S3
    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': os.getenv("BUCKET_NAME"), 'Key': filename},
        ExpiresIn=3600
    )
    print(presigned_url)

    return JSONResponse(status_code=201, content=jsonable_encoder({"url": presigned_url}))


@app.post("/insert_data")
async def insert_data(db: Session = Depends(get_db)):
    db.add(Category(id="06e0da01-57fd-4441-95be-0d25c764ea57", name="category1", icon="icon1", slug="category1"))
    db.add(Category(id=str(uuid4()), name="category2", icon="icon2", slug="category2"))
    db.commit()

    db.add(Product(id=str(uuid4()), name="product1", description="description1", price=10000, stockable=True,
                   stock=10, discount=10, number_views=1))
    db.add(Product(id=str(uuid4()), name="product2", description="description2", price=20000, stockable=True,
                   stock=20, discount=20, number_views=2))
    db.add(Product(id=str(uuid4()), name="product3", description="description3", price=30000, stockable=True,
                   stock=30, discount=30, number_views=3))
    new_product = Product(id=str(uuid4()), name="product4", description="description4", price=40000, stockable=True,
                          stock=40, discount=40, number_views=4)
    db.add(new_product)
    db.commit()
    category_to_product = db.query(Category).filter(Category.id == "06e0da01-57fd-4441-95be-0d25c764ea57").first()
    new_product.add_categories([category_to_product], db=db)
    return JSONResponse(status_code=201, content=jsonable_encoder({"message": "INSERT DATA SUCCESS"}))
