"""kwek URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from graphql_playground.views import GraphQLPlaygroundView

from kwek_auth import schema

urlpatterns = [
    path('devadmin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('kwek_auth.urls')),
    path("v1/kwekql", csrf_exempt(GraphQLView.as_view())),
    path("v2/graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path("v1/graphql", csrf_exempt(GraphQLPlaygroundView.as_view(endpoint="kwekql"))),
]
