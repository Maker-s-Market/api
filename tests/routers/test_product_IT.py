# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import StaticPool
#
# from db.database import get_db, Base
# from main import app
#
# SQLALCHEMY_DATABASE_URL = "sqlite://"
#
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False},
#     poolclass=StaticPool,
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# Base.metadata.create_all(bind=engine)
#
#
# def override_get_db():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# app.dependency_overrides[get_db] = override_get_db
#
# client = TestClient(app)
#
#
# def test_create_product():
#     response = client.post("/product", json={"name": "product1", "description": "product1's description", "price": 12.5,
#                                              "stockable": True, "stock": 2, "discount": 0, "categories": []})
#
#     assert response.status_code == 201, response.text
#
#     data = response.json()
#     assert data["name"] == "product1"
#     assert data["description"] == "product1's description"
#     assert data["price"] == 12.5
#     assert data["stockable"] == True
#     assert data["stock"] == 2
#     assert data["discount"] == 0
#     assert data["categories"] == []
#
#
# def test_put_not_existing_product():
#     response = client.put("/product/1",
#                           json={"name": "product1", "description": "product1's description", "price": 12.5,
#                                 "stockable": True, "stock": 2, "discount": 0, "categories": []})
#
#     assert response.status_code == 404, response.text
#     assert response.json() == {'detail': 'Product not found'}
#
#
# def test_put_existing_product():
#     response = client.post("/product", json={"name": "product1", "description": "product1's description", "price": 12.5,
#                                              "stockable": True, "stock": 2, "discount": 0, "categories": []})
#
#     data = response.json()
#     product_id = data["id"]
#
#     # # response = client.put("/product/" + str(product_id), json={"name": "product1_edit",
#     #                                                            "description": "product1's description", "price": 12.5,
#     #                                                            "stockable": True, "stock": 2, "discount": 0,
#     #                                                            "categories": []})
#     #
#     # assert response.status_code == 200, response.text
#     # assert response["name"] == "product1_edit"
#     # assert response["description"] == "product1's description"
#     # assert response["price"] == 12.5
#     # assert response["stockable"] == True
#     # assert response["stock"] == 2
#     # assert response["discount"] == 0
#     # assert response["categories"] == []
#
# #
# # def test_put_existing_product(self):
# #     client = TestClient(app)
# #
# #     client.post("/product",
# #         json = {
# #             "name": "product1",
# #             "description": "product1's description",
# #             "price": 12.5,
# #             "stockable": True,
# #             "stock": 2,
# #             "categories": []
# #         }
# #     )
# #
# #     response = client.post("/product",
# #         json = {
# #             "name": "product1",
# #             "description": "product1's description",
# #             "price": 12.5,
# #             "stockable": True,
# #             "stock": 2,
# #             "categories": []
# #         }
# #     )
# #
# #     assert response.status_code == 400, response.text
# #     assert response.json() == {'detail' : 'Error creating product'}
# #
# # def test_wrong_category(self):
# #     client = TestClient(app)
# #
# #     response = client.post("/product",
# #         json = {
# #             "name": "product1",
# #             "description": "product1's description",
# #             "price": 12.5,
# #             "stockable": True,
# #             "stock": 2,
# #             "categories": [{
# #                 "id": "non existent id"
# #             }]
# #         }
# #     )
# #
# #     assert response.status_code == 404
# #
# # def test_get_product(self):
# #
# #     client = TestClient(app)
# #
# #     response = client.post("/product",
# #         json = {
# #             "name": "product1",
# #             "description": "product1's description",
# #             "price": 12.5,
# #             "stockable": True,
# #             "stock": 2,
# #             "categories": []
# #         }
# #     )
# #
# #     data = response.json()
# #     product_id = data["id"]
# #
# #     response = client.get("/product/" + str(product_id))        #ig this could go wrong
# #
# #     assert response.status_code == 200
# #
# #     data = response.json()
# #
# #     assert data["id"] == str(product_id)
# #     assert data["name"] == "product1"
# #     assert data["description"] == "product1's description"
# #     assert data["price"] == 12.5
# #     assert data["stockable"] == True
# #     assert data["stock"] == 2
# #     assert data["categories"] == []
# #
# #     pass
