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
from .models import Category, Subcategory, Keyword, Product, ProductImage, ProductOption, ProductPromotion, Rating
from .model_object_type import UserType, SellerProfileType, CategoryType, SubcategoryType, KeywordType, ProductType, ProductImageType
from .model_object_type import ProductOptionType,ProductPromotionType,RatingType
from .auth_mutation import CreateUser, ResendVerification, VerifyUser, LoginUser, VerifyToken, RevokeToken, RefreshToken, SendPasswordResetEmail, ChangePassword, StartSelling
from .auth_mutation import TestToken, AccountNameRetrieval, SellerVerification, CompleteSellerVerification, UserAccountUpdate, UserPasswordUpdate, StoreUpdate, StoreLocationUpdate
from .query import Query 
from .category_subcategory_mutation import AddProductCategory, GetCategorysSubcategory, GetAllCategorysSubcategory,AddMultipleProductCategory


class AuthMutation(graphene.ObjectType):
    pass



class Mutation(AuthMutation, graphene.ObjectType):
    create_user = CreateUser.Field()
    resend_verification = ResendVerification.Field()
    verify_user = VerifyUser.Field()
    login_user = LoginUser.Field()
    verify_token = VerifyToken.Field()
    revoke_token = RevokeToken.Field()
    send_password_reset_email = SendPasswordResetEmail.Field()
    change_password = ChangePassword.Field()
    refresh_token = RefreshToken.Field()
    test_token = TestToken.Field()
    start_selling = StartSelling.Field()
    account_name_retrieval = AccountNameRetrieval.Field()
    seller_verification = SellerVerification.Field()
    complete_seller_verification = CompleteSellerVerification.Field()
    user_account_update = UserAccountUpdate.Field()
    user_password_update = UserPasswordUpdate.Field()
    store_update = StoreUpdate.Field()
    store_location_update = StoreLocationUpdate.Field()
    add_product_category = AddProductCategory.Field()
    get_categorys_subcategories = GetCategorysSubcategory.Field()
    get_all_categorys_subcategories = GetAllCategorysSubcategory.Field()
    add_multiple_product_category = AddMultipleProductCategory.Field()
    




schema = graphene.Schema(query=Query, mutation=Mutation)