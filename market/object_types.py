from graphene_django import DjangoObjectType, DjangoListField
from .models import *

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