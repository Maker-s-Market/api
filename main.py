import os
from contextlib import asynccontextmanager

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, Request, UploadFile, File, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse

from db.create_database import create_tables
from db.database import SessionLocal
from routers import product, category, insert_data, auth, ratingUser, review, user, ratingProduct, wishlist


@asynccontextmanager
async def lifespan(app):
    create_tables()
    yield


description = """
COLOCAR MORE INFORMATION THE PLATAFORME 

Some useful links:
<br> - [Makers Market Repository](https://github.com/Maker-s-Market/)
<br> - [Makers Market Documentation](https://maker-s-market.github.io/documentation/)
<br> - [Makers Market Jira](https://es-proj.atlassian.net/jira/software/projects/KAN/boards/1)
"""

tags_metadata = [
    {
        "name": "Home Page",
        "description": ""
    },
    {
        "name": "Authentication and Authorization",
        "description": "Authentication verifies the user's identity, while authorization defines what an "
                       "authenticated user can do within the system."
    },

    {
        "name": "User",
        "description": "...."
    },
    {
        "name": "Category",
        "description": "...."
    },
    {
        "name": "Product",
        "description": "...."
    },
    {
        "name": "Review",
        "description": "...."
    },
    {
        "name": "Rating The Product",
        "description": "...."
    },
    {
        "name": "Rating The User",
        "description": "....",
    },
    {
        "name": "Wishlist",
        "description": "...."
    },
    {
        "name": "Image",
        "description": "...."
    },

]

app = FastAPI(openapi_url="/openapi.json", docs_url="/docs", redoc_url="/redoc",
              lifespan=lifespan,
              title="Makers Market API",
              description=description,
              openapi_tags=tags_metadata,
              version="0.0.1",
              contact={
                  "name": "Makers Market",
              },
              servers=[
                  {
                      "url": "http://localhost:8000/",
                      "description": "Local server"
                  },
                  {
                      "url": os.getenv("AWS_URL", "COLOCAR URL"),
                      "description": "AWS server"
                  }]
              )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Add routers
app.include_router(router=insert_data.router)
app.include_router(router=auth.router)
app.include_router(router=user.router)
app.include_router(router=category.router)
app.include_router(router=product.router)
app.include_router(router=review.router)
app.include_router(router=ratingProduct.router)
app.include_router(router=ratingUser.router)
app.include_router(router=wishlist.router)

load_dotenv(".aws")
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


@app.get("/health")
async def main():
    return {"Hello": "from makers market AWS"}


@app.get("/", tags=["Home Page"])
async def main():
    return RedirectResponse(url="/docs", status_code=status.HTTP_302_FOUND)


@app.post("/api/uploadfile/", tags=["Images"])
async def create_upload_file(file: UploadFile = File(...)):
    # Generate a unique filename for the uploaded file
    filename = file.filename

    # Upload the file to the S3 bucket
    s3.upload_fileobj(file.file, os.getenv("BUCKET_NAME"), filename)

    # Generate a pre-signed URL to access the image in S3
    pre_signed_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': os.getenv("BUCKET_NAME"), 'Key': filename},
        ExpiresIn=3600
    )

    return JSONResponse(status_code=201, content=jsonable_encoder({"url": pre_signed_url}))
