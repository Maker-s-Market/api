import pytest

from main import app
from models.category import Category
from tests.test_sql_app import TestingSessionLocal
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def load_data():
    db = TestingSessionLocal()
    db.add(Category(id="06e0da01-57fd-4441-95be-0d25c764ea57", name="Category1x", icon="icon1", slug="category1x"))
    db.commit()
    db.close()


def test_create_category():
    response = client.post("/category", json={"name": "Category1", "icon": "icon1"})

    assert response.status_code == 201, response.text

    data = response.json()
    assert data["name"] == "Category1"
    assert data["icon"] == "icon1"
    assert data["slug"] == "category1"
    assert data["number_views"] == 0


def test_create_category_with_same_name():
    response = client.post("/category", json={"name": "Category1", "icon": "icon1"})

    assert response.status_code == 400, response.text
    assert response.json() == {'detail': 'Category already exists'}


def test_put_not_existing_category():
    response = client.put("/category/1", json={"name": "Category1", "icon": "icon1"})

    assert response.status_code == 404, response.text
    assert response.json() == {'detail': 'Category not found'}


def test_put_existing_category():
    response = client.put("/category/06e0da01-57fd-4441-95be-0d25c764ea57",
                          json={"name": "Category1Edit", "icon": "icon1"})

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["name"] == "Category1Edit"
    assert data["icon"] == "icon1"
    assert data["slug"] == "category1edit"
    assert data["number_views"] == 0
    assert data["created_at"] != data["updated_at"]


def test_get_all_categories():
    response = client.get("/categories")

    assert response.status_code == 200, response.text

    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Category1Edit"
    assert data[0]["icon"] == "icon1"
    assert data[0]["slug"] == "category1edit"
    assert data[0]["number_views"] == 0

    assert data[1]["name"] == "Category1"
    assert data[1]["icon"] == "icon1"
    assert data[1]["slug"] == "category1"
    assert data[1]["number_views"] == 0


def test_get_category_by_id():
    response = client.get("/category/06e0da01-57fd-4441-95be-0d25c764ea57")

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["name"] == "Category1Edit"
    assert data["icon"] == "icon1"
    assert data["slug"] == "category1edit"
    assert data["number_views"] == 1
    assert data["created_at"] != data["updated_at"]


def test_get_category_by_id_not_existing():
    response = client.get("/category/1")

    assert response.status_code == 404, response.text
    assert response.json() == {'detail': 'Category not found'}


def test_get_top_category():
    response = client.get("/top/category")

    assert response.status_code == 200, response.text

    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Category1Edit"
    assert data[0]["icon"] == "icon1"
    assert data[0]["slug"] == "category1edit"
    assert data[0]["number_views"] == 1

    assert data[1]["name"] == "Category1"
    assert data[1]["icon"] == "icon1"
    assert data[1]["slug"] == "category1"
    assert data[1]["number_views"] == 0


def test_delete_not_existing_category():
    response = client.delete("/category/1")

    assert response.status_code == 404, response.text
    assert response.json() == {'detail': 'Category not found'}


def test_delete_existing_category():
    response = client.delete("/category/06e0da01-57fd-4441-95be-0d25c764ea57")

    assert response.status_code == 200, response.text
    assert response.json() == {'message': 'DELETE DATA SUCCESS'}

    verify_response = client.get("/category/06e0da01-57fd-4441-95be-0d25c764ea57")
    assert verify_response.status_code == 404, verify_response.text
    assert verify_response.json() == {'detail': 'Category not found'}

