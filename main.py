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
from routers import (product, category, insert_data, auth, ratingUser, review, user, ratingProduct, wishlist, orders,
                     statistics, payment)


@asynccontextmanager
async def lifespan(app):
    create_tables()
    yield


description = """Makers Market is an innovative marketplace that bridges the gap between creative sellers and 
enthusiastic buyers. Our platform is designed to empower users to both sell their unique products and discover a 
diverse range of items from other community members.

Discover more about Makers Market:
<br> - [Makers Market Repository](https://github.com/Maker-s-Market/)
<br> - [Makers Market Documentation](https://maker-s-market.github.io/documentation/)
<br> - [Makers Market Jira](https://es-proj.atlassian.net/jira/software/projects/KAN/boards/1)
"""

tags_metadata = [
    {
        "name": "Authentication and Authorization",
        "description": "Authentication verifies the user's identity, while authorization defines what an "
                       "authenticated user can do within the system."
    },

    {
        "name": "User",
        "description": "Handles user profiles, profile management, and user-specific operations within the marketplace"
    },
    {
        "name": "Category",
        "description": "Manages product categories, enabling users to browse and organize products based on their "
                       "classification"
    },
    {
        "name": "Product",
        "description": "Covers all aspects of product management, from listing new products to updating and "
                       "retrieving product information."
    },
    {
        "name": "Review",
        "description": "Enables users to post reviews on products, providing feedback and experiences for other users "
                       "to reference."
    },
    {
        "name": "Rating The Product",
        "description": "Allows users to rate products, contributing to an overall product rating system that helps "
                       "others in making purchasing decisions."
    },
    {
        "name": "Rating The User",
        "description": "Facilitates the rating of users, particularly sellers, to maintain a trustworthy and reliable "
                       "user community.",
    },
    {
        "name": "Wishlist",
        "description": "Provides functionality for users to add products to a personal wishlist, aiding in future "
                       "purchase planning."
    },
    {
        "name": "Order",
        "description": "Handles all order-related processes, including order placement, tracking, and history "
                       "management for both buyers and sellers."
    },
    {
        "name": "Image",
        "description": "Manages the uploading, storing, and retrieval of product images, enhancing the visual "
                       "representation of products."
    },
    {
        "name": "Statistics",
        "description": "Gathers and presents statistical data on various aspects of the marketplace, such as sales "
                       "trends, popular products, and user engagement."
    },
    {
        "name": "Payment",
        "description": "Handles payment processing, including support for multiple payment methods and transaction "
                       "security."
    }

]

app = FastAPI(openapi_url="/api/openapi.json", docs_url="/api/docs", redoc_url="/api/redoc",
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
                      "url": "http://localhost:8000/api",
                      "description": "Local server"
                  },
                  {
                      "url": os.getenv("AWS_URL", "COLOCAR URL") + "/api",
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
app.include_router(prefix="/api", router=insert_data.router)
app.include_router(prefix="/api", router=auth.router)
app.include_router(prefix="/api", router=product.router)
app.include_router(prefix="/api", router=category.router)
app.include_router(prefix="/api", router=user.router)
app.include_router(prefix="/api", router=review.router)
app.include_router(prefix="/api", router=ratingUser.router)
app.include_router(prefix="/api", router=ratingProduct.router)
app.include_router(prefix="/api", router=wishlist.router)
app.include_router(prefix="/api", router=orders.router)
app.include_router(prefix="/api", router=statistics.router)
app.include_router(prefix="/api", router=payment.router)

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


@app.get("/api/health")
async def main():
    return {"Hello": "from makers market AWS"}


# @app.get("/", tags=["Home Page"])
# async def main():
#     return RedirectResponse(url="/docs", status_code=status.HTTP_302_FOUND)
#

@app.post("/api/uploadfile/", tags=["Image"])
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
