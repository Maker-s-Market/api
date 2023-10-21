from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


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


# def test_put_existing_product_existing_category():
#     response = client.post("/category",
#                            json={
#                                "name": "category1",
#                                "icon": "icon1"
#                            })
#
#     category1_id = response.json()["id"]
#
#     response = client.post("/category",
#                            json={
#                                "name": "category2",
#                                "icon": "icon2"
#                            })
#
#     category2_id = response.json()["id"]
#
#     response = client.post("/product",
#                            json={
#                                "name": "product1",
#                                "description": "product1's description",
#                                "price": 12.5,
#                                "stockable": True,
#                                "stock": 2,
#                                "discount": 0,
#                                "categories": []
#                            }
#                            )
#
#     product_id = response.json()["id"]
#
#     response = client.put("/product/" + str(product_id),
#                           json={
#                               "name": "product1",
#                               "description": "product1's description",
#                               "price": 12.5,
#                               "stockable": True,
#                               "stock": 2,
#                               "discount": 0,
#                               "categories": [
#                                   {
#                                       "id": str(category1_id)
#                                   },
#                                   {
#                                       "id": str(category2_id)
#                                   }
#                               ]
#                           })
#
#     assert response.status_code == 200, response.text
#     data = response.json()
#
#     assert data["id"] == str(product_id)
#     assert data["name"] == "product1"
#     assert data["description"] == "product1's description"
#     assert data["price"] == 12.5
#     assert data["stockable"] == True
#     assert data["stock"] == 2
#     assert data["discount"] == 0
#
#     assert len(data["categories"]) == 2
#     assert data["categories"][0]["id"] == category1_id
#     assert data["categories"][1]["id"] == category2_id
#     assert data["categories"][0]["name"] == "category1"


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
