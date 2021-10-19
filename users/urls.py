from django.urls import path
from graphene_django.views import GraphQLView
from .schema import schema
from . import views

urlpatterns = [
    path("email_verification/", views.verify_email, name = "login"),
    path("", views.home_redirect, name = "Home Page"),
]