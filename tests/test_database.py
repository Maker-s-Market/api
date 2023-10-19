from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import get_db, Base
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_product():
    response = client.post("/product", json={"name": "product1", "description": "product1's description", "price": 12.5,
                                             "stockable": True, "stock": 2, "categories": []})

    assert response.status_code == 201, response.text

    data = response.json()
    assert data["name"] == "product1"
    assert data["description"] == "product1's description"
    assert data["price"] == 12.5
    assert data["stockable"] == True
    assert data["stock"] == 2
    assert data["categories"] == []
