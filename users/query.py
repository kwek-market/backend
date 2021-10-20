import graphene
import jwt
from graphene_django import DjangoObjectType, DjangoListField
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations
from django.conf import settings
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from .validate import validate_email, validate_passwords, validate_user_passwords
from .sendmail import send_confirmation_email, user_loggedIN, expire_token, send_password_reset_email, refresh_user_token
from .models import ExtendUser, SellerProfile
from graphql_jwt.utils import jwt_encode, jwt_payload
from django.contrib.auth import authenticate
from graphql_jwt.shortcuts import create_refresh_token, get_token
import time
import datetime;
from .send_post import send_post_request
from django.contrib.auth.models import auth
from django.contrib.auth.hashers import check_password
from .models import Category,Subcategory,Keyword,Product,ProductImage,ProductOption,ProductPromotion,Rating
from .model_object_type import UserType,SellerProfileType,CategoryType,SubcategoryType,KeywordType,ProductType,ProductImageType
from .model_object_type import ProductOptionType,ProductPromotionType,RatingType


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