import graphene
import jwt
from graphene_django import DjangoObjectType, DjangoListField
from users.sendmail import send_confirmation_email, user_loggedIN, expire_token, send_password_reset_email, refresh_user_token
from users.models import ExtendUser, SellerProfile
from .models import Category, Subcategory, Keyword, Product, ProductImage, ProductOption, ProductPromotion, Rating
from django.contrib.auth import get_user_model
 

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()

class SellerProfileType(DjangoObjectType):
    class Meta:
        model = SellerProfile
        fields = ("user","firstname","lastname","phone_number","shop_name","shop_url","shop_address","state","city",
        "lga","landmark","how_you_heard_about_us","accepted_policy","store_banner_url","store_description","prefered_id",
        "prefered_id_url","bvn","bank_name","bank_account_number","bank_account_name","seller_is_verified","bank_account_is_verified",
        "bank_sort_code","accepted_vendor_policy")



class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id","name")
        
class SubcategoryType(DjangoObjectType):
    class Meta:
        model = Subcategory
        fields = ("id","name","category","parentcategory","childcategory","parent","child") 

class KeywordType(DjangoObjectType):
    class Meta:
        model = Keyword
        fields = ("id","keyword")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id","product_title","user","category","brand","product_weight","short_description",
        "charge_five_percent_vat","return_policy","warranty","color","gender","keyword",
        "clicks","promoted") 

class ProductImageType(DjangoObjectType):
    class Meta:
        model = ProductImage
        fields = ("id","product","image_url")

class ProductOptionType(DjangoObjectType):
    class Meta:
        model = ProductOption
        fields = ("id","product","size","quantity","price","discounted_price","option_total_price") 

class ProductPromotionType(DjangoObjectType):
    class Meta:
        model = ProductPromotion
        fields = ("id","product","start_date","end_date","days","active","amount","reach","link_clicks")

class RatingType(DjangoObjectType):
    class Meta:
        model = Rating
        fields = ("id","product","rating","comment","name","email","rated_at")