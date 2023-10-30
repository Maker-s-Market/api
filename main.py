import os
from contextlib import asynccontextmanager
from uuid import uuid4

import boto3
from fastapi import FastAPI, Depends, Request, UploadFile, File, APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from pydantic import BaseModel

from db.create_database import create_tables
from db.database import get_db, SessionLocal
from models.category import Category
from models.product import Product
from routers import product, category, insert_data, user

from auth.JWTBearer import JWTBearer

@asynccontextmanager
async def lifespan(app):
    create_tables()
    yield


description = """
Some useful links:
<br> - [Makers Market Repository](https://github.com/Maker-s-Market/)
<br> - [Makers Market Documentation](https://maker-s-market.github.io/documentation/)
<br> - [Makers Market Jira](https://es-proj.atlassian.net/jira/software/projects/KAN/boards/1)
"""
app = FastAPI(lifespan=lifespan,
              title="Makers Market API",
              description=description,
              version="0.0.1",
              docs_url="/docs",
              redoc_url="/redoc",
              openapi_url="/openapi.json",
              contact={
                  "name": "Makers Market",
              },
              servers=[
                  {
                      "url": "http://localhost:8000",
                      "description": "Local server"
                  }]
              )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(insert_data.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(user.router)

load_dotenv(".aws")
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

    return JSONResponse(status_code=201, content=jsonable_encoder({"url": presigned_url}))

