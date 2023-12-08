import os
from uuid import uuid4

import pytest
import math

from fastapi.testclient import TestClient

from main import app
from models.category import Category
from models.product import Product
from models.user import User
from tests.test_sql_app import TestingSessionLocal
from dotenv import load_dotenv

load_dotenv()  # import pytest.ini env variables
COGNITO_USER_CLIENT_ID = os.getenv("COGNITO_USER_CLIENT_ID")

client = TestClient(app)


def get_client_id():
    return COGNITO_USER_CLIENT_ID


@pytest.fixture(scope="module", autouse=True)
def load_data():
    db = TestingSessionLocal()
    db.query(Category).delete()
    db.query(Product).delete()
    db.query(User).delete()
    user1 = User(id=str(uuid4()), name="Bruna", username="brums21", email="brums21.10@gmail.com", city="pombal",
                 region="nao existe", photo="", role="Premium")
    user2 = User(id=str(uuid4()), name="Mariana", username="mariana", email="marianaandrade@ua.pt", city="aveiro",
                 region="nao sei", photo="", role="Premium")
    db.add(user1)
    db.add(user2)
    db.add(Category(id="06e0da01-57fd-4441-95be-0d25c764ea57", name="Category1x", icon="icon1", slug="category1x"))
    db.add(Product(id="06e0da01-57fd-2227-95be-0d25c764ea56", name="random product 1", description="some description 1",
                   price=12.0, stockable=False, user_id=user1.id))
    db.add(Product(id="06e0da01-57fd-2228-95be-0d25c764ea57", name="random product 2", description="some description 2",
                   price=11.0, stockable=True, user_id=user2.id))
    db.add(Product(id="06e0da01-57fd-2229-95be-123455555566", name="random product 3", description="some description 3",
                   price=10.0, stockable=True, user_id="123456789023456789"))

    db.commit()
    db.close()


def test_normal_post_product_success():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.post("/api/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token})

    assert response.status_code == 201, response.text

    data = response.json()
    assert data["user_id"] == response.json()["user_id"]
    assert data["name"] == "product1"
    assert data["description"] == "product1's description"
    assert math.isclose(data["price"], 12.5, abs_tol=0.1)
    assert data["stockable"] == True
    assert data["stock"] == 2
    assert data["discount"] == 0
    assert data["categories"] == []
    assert data["image"] == "image1"


def test_post_product_no_token():
    response = client.post("/api/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           })

    assert response.status_code == 403
    assert response.json() == {'detail': 'Not authenticated'}


def test_post_product_but_wrong_category():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()

    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.post("/api/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [{
                                   "id": "non existent id"
                               }],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token})

    assert response.status_code == 404


def test_get_product():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()

    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.post("/api/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token})

    data = response.json()
    product_id = data["id"]

    response = client.get("/api/product/" + str(product_id))  # ig this could go wrong

    assert response.status_code == 200

    data_product = response.json()["product"]
    data_user = response.json()["user"]

    assert data_product["id"] == str(product_id)
    assert data_product["name"] == "product1"
    assert data_product["description"] == "product1's description"
    assert math.isclose(data_product["price"], 12.5, abs_tol=0.1)
    assert data_product["stockable"] == True
    assert data_product["stock"] == 2
    assert data_product["discount"] == 0
    assert data_product["categories"] == []
    assert data_product["image"] == "image1"

    assert data_user["id"] == data["user_id"]
    assert data_user["name"] == "Bruna"
    assert data_user["username"] == "brums21"


def test_get_product_not_existing_id_the_product():
    mock_id = "some random id string"
    response = client.get("/api/product/" + mock_id)
    assert response.status_code == 404, response.text == "Product not found"


def test_get_product_not_existing_id_the_user():
    response = client.get("/api/product/06e0da01-57fd-2229-95be-123455555566")
    assert response.status_code == 404, response.text == "User not found"


# PUT TESTS
def test_put_not_existing_product():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()

    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.put("/api/product/1",
                          json={
                              "name": "product1",
                              "description": "product1's description",
                              "price": 12.5,
                              "stockable": True,
                              "stock": 2,
                              "discount": 0,
                              "categories": [],
                              "image": "image1"
                          },
                          headers={"Authorization": "Bearer " + token}
                          )

    assert response.status_code == 404, response.text
    assert response.json() == {'detail': 'Product not found'}


def test_put_existing_product_no_category():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()

    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.post("/api/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token}
                           )

    product_id = response.json()["id"]

    response = client.put("/api/product/" + str(product_id),
                          json={
                              "name": "product123",
                              "description": "product123's description",
                              "price": 14.5,
                              "stockable": False,
                              "stock": 0,
                              "discount": 0,
                              "categories": [],
                              "image": "image1"
                          },
                          headers={"Authorization": "Bearer " + token}
                          )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["id"] == str(product_id)
    assert data["name"] == "product123"
    assert data["description"] == "product123's description"
    assert math.isclose(data["price"], 14.5, abs_tol=0.1)
    assert data["stockable"] == False
    assert data["stock"] == 0
    assert data["discount"] == 0
    assert data["categories"] == []
    assert data["image"] == "image1"


def test_put_existing_product_no_existing_category():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()

    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.post("/api/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token}
                           )

    product_id = response.json()["id"]

    response = client.put("/api/product/" + str(product_id),
                          json={
                              "name": "product123",
                              "description": "product123's description",
                              "price": 14.5,
                              "stockable": False,
                              "stock": 0,
                              "discount": 0,
                              "categories": [{
                                  "id": "some non existing id"
                              }],
                              "image": "image1"
                          },
                          headers={"Authorization": "Bearer " + token}
                          )

    assert response.status_code == 404, response.text
    assert response.json() == {'detail': 'Category not found'}


def test_put_existing_product_existing_category():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()

    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.post("/api/category",
                           json={
                               "name": "category1edit",
                               "icon": "icon1"
                           })

    category1_id = response.json()["id"]

    response = client.post("/api/category",
                           json={
                               "name": "category2edit",
                               "icon": "icon2"
                           })

    category2_id = response.json()["id"]

    response = client.post("/api/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token}
                           )

    product_id = response.json()["id"]

    response = client.put("/api/product/" + str(product_id),
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
                              ],
                              "image": "image1"
                          },
                          headers={"Authorization": "Bearer " + token})

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["id"] == str(product_id)
    assert data["name"] == "product1"
    assert data["description"] == "product1's description"
    assert math.isclose(data["price"], 12.5, abs_tol=0.1)
    assert data["stockable"] == True
    assert data["stock"] == 2
    assert data["discount"] == 0
    assert data["image"] == "image1"

    assert len(data["categories"]) == 2
    assert data["categories"][0]["id"] == category1_id or data["categories"][0]["id"] == category2_id
    assert data["categories"][1]["id"] == category2_id or data["categories"][1]["id"] == category1_id


def test_put_not_authenticated():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()

    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.post("/api/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token}
                           )

    product_id = response.json()["id"]

    response = client.put("/api/product/" + str(product_id),
                          json={
                              "name": "product1",
                              "description": "product1's description",
                              "price": 12.5,
                              "stockable": True,
                              "stock": 2,
                              "discount": 0,
                              "categories": [],
                              "image": "image1"
                          })
    assert response.status_code == 403
    assert response.json() == {'detail': 'Not authenticated'}


def test_put_not_allowed():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()

    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.post("/api/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token}
                           )

    product_id = response.json()["id"]

    response = client.post("/api/auth/sign-in", json={
        "identifier": "mariana",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.put("/api/product/" + str(product_id),
                          json={
                              "name": "product1",
                              "description": "product1's description",
                              "price": 12.5,
                              "stockable": True,
                              "stock": 2,
                              "discount": 0,
                              "categories": [],
                              "image": "image1"
                          },
                          headers={"Authorization": "Bearer " + token}
                          )

    assert response.status_code == 403
    assert response.json() == {'detail': 'Only the user can change its products'}


def test_delete_existing_product():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]
    response = client.post("/api/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token}
                           )

    product_id = response.json()["id"]

    response = client.delete("/api/product/" + product_id, headers={"Authorization": "Bearer " + token})

    assert response.status_code == 200
    assert response.json() == {"message": "Product deleted"}


def test_delete_non_existing_product():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()

    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    id = "some non-existing id"

    response = client.delete("/api/product/" + id, headers={"Authorization": "Bearer " + token})

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_delete_not_authenticated():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]
    response = client.post("/api/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token}
                           )

    product_id = response.json()["id"]

    response = client.delete("/api/product/" + product_id)

    assert response.status_code == 403
    assert response.json() == {'detail': 'Not authenticated'}


def test_delete_not_owner():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()

    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]
    response = client.post("/api/product",
                           json={
                               "name": "product1",
                               "description": "product1's description",
                               "price": 12.5,
                               "stockable": True,
                               "stock": 2,
                               "discount": 0,
                               "categories": [],
                               "image": "image1"
                           },
                           headers={"Authorization": "Bearer " + token}
                           )

    product_id = response.json()["id"]

    response = client.post("/api/auth/sign-in", json={
        "identifier": "mariana",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.delete("/api/product/" + str(product_id), headers={"Authorization": "Bearer " + token})

    assert response.status_code == 403
    assert response.json() == {'detail': 'Only the user can change its products'}


def test_filter_product():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    client.post("/api/product",
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
                },
                headers={"Authorization": "Bearer " + token}
                )

    client.post("/api/product",
                json={
                    "name": "product2",
                    "description": "product2's description",
                    "price": 15.5,
                    "stockable": False,
                    "stock": 0,
                    "discount": 50,
                    "categories": []
                },
                headers={"Authorization": "Bearer " + token}
                )

    response = client.get(
        "/api/product?q=" + str(1) + "&limit=" + str(4) + "&price_min=" + str(3) + "&price_max=" + str(20) +
        "&location=" + str("") + "&sort=price_asc&discount=" + str(0))

    data = response.json()

    assert response.status_code == 200, response.text
    assert len(data) == 4


def test_filter_product_category_not_found():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    client.post("/api/product",
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
                },
                headers={"Authorization": "Bearer " + token}
                )

    response = client.get("/api/product" +
                          "?q=" + str(1) +
                          "&limit=" + str(1) +
                          "&price_min=" + str(3) +
                          "&price_max=" + str(20) +
                          "&location=" + str("") +
                          "&sort=" + "price_asc" +
                          "&discount=" + str(0) +
                          "&category_id=" + "some unknown category id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}


def test_filter_product_invalid_price_range():
    response = client.get("/api/product" +
                          "?q=" + str(1) +
                          "&limit=" + str(1) +
                          "&price_min=" + str(20) +
                          "&price_max=" + str(3) +
                          "&location=" + str("") +
                          "&sort=" + "price_asc" +
                          "&discount=" + str(0))

    assert response.status_code == 400
    assert response.json() == {'detail': 'Invalid price range'}


# this
def test_product_location():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    client.post("/api/product",
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
                },
                headers={"Authorization": "Bearer " + token}
                )

    client.post("/api/product",
                json={
                    "name": "product2",
                    "description": "product2's description",
                    "price": 15.5,
                    "stockable": False,
                    "stock": 0,
                    "discount": 50,
                    "categories": []
                },
                headers={"Authorization": "Bearer " + token}
                )

    response = client.get("/api/product" +
                          "?q=" + str(1) +
                          "&limit=" + str(2) +
                          "&price_min=" + str(3) +
                          "&price_max=" + str(20) +
                          "&location=" + str("pombal") +
                          "&sort=" + "price_asc" +
                          "&discount=" + str(0))

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_product_no_location():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/api/auth/sign-in", json={
        "identifier": "brums21",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    client.post("/api/product",
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
                },
                headers={"Authorization": "Bearer " + token}
                )

    client.post("/api/product",
                json={
                    "name": "product2",
                    "description": "product2's description",
                    "price": 15.5,
                    "stockable": False,
                    "stock": 0,
                    "discount": 50,
                    "categories": []
                },
                headers={"Authorization": "Bearer " + token}
                )

    response = client.get("/api/product" +
                          "?q=" + str(1) +
                          "&limit=" + str(2) +
                          "&price_min=" + str(3) +
                          "&price_max=" + str(20) +
                          "&location=" + str("some random location") +
                          "&sort=" + "price_asc" +
                          "&discount=" + str(0))

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_filter_product_invalid_sort():
    response = client.get("/api/product" +
                          "?q=" + str(1) +
                          "&limit=" + str(1) +
                          "&price_min=" + str(3) +
                          "&price_max=" + str(20) +
                          "&sort=" + "some unknown sorte" +
                          "&discount=" + str(0))

    assert response.status_code == 400
    assert response.json() == {'detail': 'Invalid sort parameter'}


def test_get_top_products():
    response = client.get("/api/product/top/4")

    assert response.status_code == 200, response.text

    data = response.json()
    assert len(data) == 4


def test_put_products_available_not_auth():
    response = client.put("/api/product/06e0da01-57fd-2227-95be-0d25c764ea57/available", json={"available": True})

    assert response.status_code == 403
    assert response.json() == {'detail': 'Not authenticated'}


def test_put_products_available_not_owner():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/api/auth/sign-in", json={
        "identifier": "marianaandrade@ua.pt",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.put("/api/product/06e0da01-57fd-2229-95be-123455555566/available?available=true",
                          headers={"Authorization": "Bearer " + token})

    assert response.status_code == 403
    assert response.json() == {'detail': "Only the user can change their product's available"}


def test_put_products_available_not_existing_product():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/api/auth/sign-in", json={
        "identifier": "marianaandrade@ua.pt",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.put("/api/product/06e0da01-57fd-2227-95be-0d25c764ea57/available?available=true",
                          headers={"Authorization": "Bearer " + token})

    assert response.status_code == 404
    assert response.json() == {'detail': "Product not found"}


def test_put_products_available_already_available():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/api/auth/sign-in", json={
        "identifier": "marianaandrade@ua.pt",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.put("/api/product/06e0da01-57fd-2228-95be-0d25c764ea57/available?available=true",
                          headers={"Authorization": "Bearer " + token})

    assert response.status_code == 400
    assert response.json() == {'detail': "Product is already in that state"}


def test_put_products_available_success():
    os.environ['COGNITO_USER_CLIENT_ID'] = get_client_id()
    response = client.post("/api/auth/sign-in", json={
        "identifier": "marianaandrade@ua.pt",
        "password": os.getenv("PASSWORD_CORRECT")
    })
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.put("/api/product/06e0da01-57fd-2228-95be-0d25c764ea57/available?available=false",
                          headers={"Authorization": "Bearer " + token})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "06e0da01-57fd-2228-95be-0d25c764ea57"
    assert data["available"] == False


def test_get_product_id_not_available():
    response = client.get("/api/product/06e0da01-57fd-2228-95be-0d25c764ea57")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Product not available'}
