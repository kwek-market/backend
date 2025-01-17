from django.urls import path
from graphene_django.views import GraphQLView

from . import views
from .schema import schema

urlpatterns = [
    path("email_verification/", views.verify_email, name="login"),
    path("", views.home_redirect, name="Home Page"),
    path(
        "delete-user-and-records/",
        views.delete_user_and_related_records,
        name="delete_user_and_related_records",
    ),
]
