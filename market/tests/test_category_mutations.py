# import uuid

# import graphene
# import pytest
# from django.conf import settings
# from graphene_django.utils.testing import GraphQLTestCase

# from market.models import Category


# # =====================================================================================================================
# # Test Case for AddCategory Mutation
# @pytest.mark.django_db
# class TestAddCategoryMutation(GraphQLTestCase):
#     GRAPHQL_URL = f"/{settings.GRAPHQL_ENDPOINT}"

#     def test_add_category(self):
#         query = """
#             mutation {
#                 addCategory(name: "Electronics", visibility: "visible", icon: "icon_url") {
#                     status
#                     message
#                     category {
#                         id
#                         name
#                     }
#                 }
#             }
#         """
#         response = self.client.post(
#             self.GRAPHQL_URL, data={"query": query}, content_type="application/json"
#         )
#         content = response.json()

#         # Assert success response
#         assert content["data"]["addCategory"]["status"] is True
#         assert (
#             content["data"]["addCategory"]["message"] == "Category added successfully"
#         )
#         assert content["data"]["addCategory"]["category"]["name"] == "Electronics"

#     def test_add_category_with_existing_name(self):
#         # Add initial category
#         Category.objects.create(
#             name="Electronics", visibility="visible", icon="icon_url"
#         )

#         query = """
#             mutation {
#                 addCategory(name: "Electronics", visibility: "visible", icon: "icon_url") {
#                     status
#                     message
#                 }
#             }
#         """
#         response = self.client.post(
#             self.GRAPHQL_URL, data={"query": query}, content_type="application/json"
#         )
#         content = response.json()

#         # Assert failure due to existing category name
#         assert content["data"]["addCategory"]["status"] is False
#         assert content["data"]["addCategory"]["message"] == "Category already exists"


# # =====================================================================================================================
# # Test Case for UpdateCategory Mutation
# @pytest.mark.django_db
# class TestUpdateCategoryMutation(GraphQLTestCase):
#     GRAPHQL_URL = f"/{settings.GRAPHQL_ENDPOINT}"
#     ruuid = uuid.uuid4()

#     def test_update_category(self):
#         category = Category.objects.create(
#             name="Electronics", visibility="visible", icon="icon_url"
#         )

#         query = (
#             """
#             mutation {
#                 updateCategory(id: "%s", name: "Updated Electronics", visibility: "hidden", icon: "new_icon") {
#                     status
#                     message
#                     category {
#                         id
#                         name
#                         visibility
#                         icon
#                     }
#                 }
#             }
#         """
#             % category.id
#         )

#         response = self.client.post(
#             self.GRAPHQL_URL, data={"query": query}, content_type="application/json"
#         )
#         content = response.json()

#         # Assert successful update
#         assert content["data"]["updateCategory"]["status"] is True
#         assert (
#             content["data"]["updateCategory"]["message"]
#             == "Category updated successfully"
#         )
#         assert (
#             content["data"]["updateCategory"]["category"]["name"]
#             == "Updated Electronics"
#         )
#         assert content["data"]["updateCategory"]["category"]["visibility"] == "hidden"
#         assert content["data"]["updateCategory"]["category"]["icon"] == "new_icon"

#     def test_update_category_with_invalid_id(self):
#         query = (
#             """
#             mutation {
#                 updateCategory(id: "%s", name: "Non-existent Category", visibility: "hidden") {
#                     status
#                     message
#                 }
#             }
            
#         """
#             % self.ruuid
#         )

#         response = self.client.post(
#             self.GRAPHQL_URL, data={"query": query}, content_type="application/json"
#         )
#         content = response.json()

#         # Assert failure due to invalid category ID
#         assert content["data"]["updateCategory"]["status"] is False
#         assert content["data"]["updateCategory"]["message"] == "Invalid id"


# # =====================================================================================================================
# # Test Case for DeleteCategory Mutation
# @pytest.mark.django_db
# class TestDeleteCategoryMutation(GraphQLTestCase):
#     GRAPHQL_URL = f"/{settings.GRAPHQL_ENDPOINT}"
#     ruuid = uuid.uuid4()

#     def test_delete_category(self):
#         category = Category.objects.create(
#             name="Electronics", visibility="visible", icon="icon_url"
#         )

#         query = (
#             """
#             mutation {
#                 deleteCategory(id: "%s") {
#                     status
#                     message
#                 }
#             }
#         """
#             % category.id
#         )

#         response = self.client.post(
#             self.GRAPHQL_URL, data={"query": query}, content_type="application/json"
#         )
#         content = response.json()

#         # Assert successful deletion
#         assert content["data"]["deleteCategory"]["status"] is True
#         assert content["data"]["deleteCategory"]["message"] == "Deleted successfully"
#         assert not Category.objects.filter(id=category.id).exists()

#     def test_delete_category_with_invalid_id(self):
#         query = ("""
#             mutation {
#                 deleteCategory(id: "%s") {
#                     status
#                     message
#                 }
#             }
#         """
#         % self.ruuid)
#         response = self.client.post(
#             self.GRAPHQL_URL, data={"query": query}, content_type="application/json"
#         )
#         content = response.json()

#         # Assert failure due to invalid category ID
#         assert content["data"]["deleteCategory"]["status"] is False
#         assert content["data"]["deleteCategory"]["message"] == "Invalid id"
