import pytest

from fastapi.testclient import TestClient

from main import app
from models.category import Category
from models.product import Product
from tests.test_sql_app import TestingSessionLocal

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def load_data():
    db = TestingSessionLocal()

    db.add(Category(id="06e0da01-57fd-4441-95be-0d25c764ea57", name="Category1x", icon="icon1", slug="category1x"))
    db.add(Product(id="06e0da01-57fd-2227-95be-0d25c764ea57", name="random product 1", description = "some description 1", price=12.0, stockable = False))
    db.add(Product(id="06e0da01-57fd-2228-95be-0d25c764ea57", name="random product 2", description = "some description 2", price=11.0, stockable = True))
    
    db.commit()
    db.close()

def test_normal_post_product():
    response = client.post("/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": []
                           })

    assert response.status_code == 201, response.text

    data = response.json()
    assert data["name"] == "product1"
    assert data["description"] == "product1's description"
    assert data["price"] == 12.5
    assert data["stockable"] == True
    assert data["stock"] == 2
    assert data["discount"] == 0
    assert data["categories"] == []


def test_post_wrong_category():
    response = client.post("/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [{
                                   "id": "non existent id"
                               }]
                           }
                           )

    assert response.status_code == 404


# GET  TESTS
def test_get_product():
    response = client.post("/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": []
                           }
                           )

    data = response.json()
    product_id = data["id"]

    response = client.get("/product/" + str(product_id))  # ig this could go wrong

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(product_id)
    assert data["name"] == "product1"
    assert data["description"] == "product1's description"
    assert data["price"] == 12.5
    assert data["stockable"] == True
    assert data["stock"] == 2
    assert data["discount"] == 0
    assert data["categories"] == []


def test_no_correct_id_product():
    mock_id = "some random id string"

    response = client.get("/product/" + mock_id)

    assert response.status_code == 404, response.text == "Product not found"


# PUT TESTS
def test_put_not_existing_product():
    response = client.put("/product/1",
                          json={
                              "name": "product1",
                              "description": "product1's description",
                              "price": 12.5,
                              "stockable": True,
                              "stock": 2,
                              "discount": 0,
                              "categories": []
                          })

    assert response.status_code == 404, response.text
    assert response.json() == {'detail': 'Product not found'}


def test_put_existing_product_no_category():
    response = client.post("/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": []
                           }
                           )

    product_id = response.json()["id"]

    response = client.put("/product/" + str(product_id),
                          json={
                              "name": "product123",
                              "description": "product123's description",
                              "price": 14.5,
                              "stockable": False,
                              "stock": 0,
                              "discount": 0,
                              "categories": []
                          })

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["id"] == str(product_id)
    assert data["name"] == "product123"
    assert data["description"] == "product123's description"
    assert data["price"] == 14.5
    assert data["stockable"] == False
    assert data["stock"] == 0
    assert data["discount"] == 0
    assert data["categories"] == []


def test_put_existing_product_no_existing_category():
    response = client.post("/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": []
                           }
                           )

    product_id = response.json()["id"]

    response = client.put("/product/" + str(product_id),
                          json={
                              "name": "product123",
                              "description": "product123's description",
                              "price": 14.5,
                              "stockable": False,
                              "stock": 0,
                              "discount": 0,
                              "categories": [{
                                  "id": "some non existing id"
                              }]
                          })

    assert response.status_code == 404, response.text
    assert response.json() == {'detail': 'Category not found'}


""" def test_put_existing_product_existing_category():
    response = client.post("/category",
                           json={
                               "name": "category1",
                               "icon": "icon1"
                           })

    category1_id = response.json()["id"]

    response = client.post("/category",
                           json={
                               "name": "category2",
                               "icon": "icon2"
                           })

    category2_id = response.json()["id"]

    response = client.post("/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": []
                           }
                           )

    product_id = response.json()["id"]

    response = client.put("/product/" + str(product_id),
                          json={
                              "name": "product1",
                              "description": "product1's description",
                              "price": 12.5,
                              "stockable": True,
                              "stock": 2,
                              "discount": 0,
                              "categories": [
                                  {
                                      "id": str(category1_id)
                                  },
                                  {
                                      "id": str(category2_id)
                                  }
                              ]
                          })

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["id"] == str(product_id)
    assert data["name"] == "product1"
    assert data["description"] == "product1's description"
    assert data["price"] == 12.5
    assert data["stockable"] == True
    assert data["stock"] == 2
    assert data["discount"] == 0

    assert len(data["categories"]) == 2
    assert data["categories"][0]["id"] == category1_id
    assert data["categories"][1]["id"] == category2_id
    assert data["categories"][0]["name"] == "category1" """


# DELETE TESTS

def test_delete_existing_product():
    response = client.post("/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": []
                           }
                           )

    product_id = response.json()["id"]

    response = client.delete("/product/" + product_id)

    assert response.status_code == 200
    assert response.json() == {"message": "Product deleted"}


def test_delete_non_existing_product():
    id = "some non-existing id"

    response = client.delete("/product/" + id)

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_filter_product():
    client.post("/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [{
                                "id": "06e0da01-57fd-4441-95be-0d25c764ea57"
                            }]
                           })

    client.post("/product",
                        json={
                            "name": "product2",
                            "description": "product2's description",
                            "price": 15.5,
                            "stockable": False,
                            "stock": 0,
                            "discount": 50,
                            "categories": []
                        })


    response = client.get("/products" + 
                        "?q=" + str(1) + 
                        "&limit=" + str(1) + 
                        "&price_min=" + str(3) +
                        "&price_max=" + str(20) +
                        "&sort=" + "price_asc" + 
                        "&discount=" + str(0))

    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 1
    assert data[0]["id"] == "06e0da01-57fd-2227-95be-0d25c764ea57"


def test_filter_product_category_not_found():

    client.post("/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [{
                                "id": "06e0da01-57fd-4441-95be-0d25c764ea57"
                            }]
                           })

    response = client.get("/products" + 
                        "?q=" + str(1) + 
                        "&limit=" + str(1) + 
                        "&price_min=" + str(3) +
                        "&price_max=" + str(20) +
                        "&sort=" + "price_asc" + 
                        "&discount=" + str(0) +
                        "&category_id=" + "some unknown category id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}

def test_filter_product_invalid_price_range():

    response = client.get("/products" + 
                        "?q=" + str(1) + 
                        "&limit=" + str(1) + 
                        "&price_min=" + str(20) +
                        "&price_max=" + str(3) +
                        "&sort=" + "price_asc" + 
                        "&discount=" + str(0))

    assert response.status_code == 400
    assert response.json() == {'detail': 'Invalid price range'}

def test_filter_product_invalid_sort():

    response = client.get("/products" + 
                        "?q=" + str(1) + 
                        "&limit=" + str(1) + 
                        "&price_min=" + str(3) +
                        "&price_max=" + str(20) +
                        "&sort=" + "some unknown sorte" + 
                        "&discount=" + str(0))

    assert response.status_code == 400
    assert response.json() == {'detail': 'Invalid sort parameter'}