import graphene
import jwt
from graphene_django import DjangoListField
from graphql_auth.schema import UserQuery, MeQuery
from django.conf import settings
from .models import ExtendUser, SellerProfile
from .model_object_type import UserType,SellerProfileType
from market.object_types import *
from market.models import *

class Query(UserQuery, MeQuery, graphene.ObjectType):
    user_data = graphene.Field(UserType, token = graphene.String())
    seller_data = graphene.Field(SellerProfileType, token = graphene.String())
    all_categories = DjangoListField(CategoryType)

    def resolve_user_data(root, info, token):
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])["username"]
        return ExtendUser.objects.get(email=email)

    def resolve_seller_data(root, info, token):
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])["username"]
        c_user = ExtendUser.objects.get(email=email)
        userid = c_user.id
        return SellerProfile.objects.get(user=userid)

    # def resolve_all_categories(root, info):
    #     return Category.objects.all()