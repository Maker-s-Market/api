from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.create_database import create_tables
from routers import product, category


@asynccontextmanager
async def lifespan(app):
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(product.router)
app.include_router(category.router)
