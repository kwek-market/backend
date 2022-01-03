import graphene
import jwt
from graphene_django import DjangoListField
from graphene_django.filter import DjangoFilterConnectionField
from graphql_auth.schema import UserQuery, MeQuery
from django.conf import settings
from .model_object_type import UserType, SellerProfileType
from market.object_types import *
from users.models import ExtendUser, SellerProfile
from django.db.models import Q
from bill.object_types import *


class Query(UserQuery, MeQuery, graphene.ObjectType):
    user_data = graphene.Field(UserType, token=graphene.String())
    seller_data = graphene.Field(SellerProfileType, token=graphene.String())

    categories = DjangoListField(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.String(required=True))
    subcategories = graphene.List(CategoryType)
    product = graphene.relay.Node.Field(ProductType)
    products = graphene.List(ProductType, search=graphene.String(), rating=graphene.Int(), keyword=graphene.List(graphene.String))
    subcribers = DjangoListField(NewsletterType)
    carts = graphene.List(CartType, token=graphene.String(), ip=graphene.String())
    wishlists = graphene.List(WishlistType, token=graphene.String(required=True))
    reviews = DjangoListField(RatingType)
    review = graphene.Field(RatingType, review_id=graphene.String(required=True))
    billing_addresses = DjangoListField(BillingType)
    billing_address = graphene.Field(PickupType, address_id=graphene.String(required=True))
    pickup_locations = DjangoListField(PickupType)
    pickup_location = graphene.Field(PickupType, location_id=graphene.String(required=True))

    def resolve_user_data(root, info, token):
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
        return ExtendUser.objects.get(email=email)

    def resolve_seller_data(root, info, token):
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
        c_user = ExtendUser.objects.get(email=email)
        userid = c_user.id
        return SellerProfile.objects.get(user=userid)

    def resolve_category(root, info, id):
        return Category.objects.get(pk=id)

    def resolve_subcategories(root, info):
        categories = Category.objects.all()
        cat_list=[]

        for category in categories:
            if category.parent:
                cat_list.append(category)
        return cat_list

    def resolve_carts(root, info, token=None, ip=None):
        if token is not None:
            email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
            user = ExtendUser.objects.get(email=email)
            if user:
                cart_item = Cart.objects.select_related("user_id", "product").filter(user_id=user)
        if ip is not None:
            cart_item = Cart.objects.select_related("user_id", "product").filter(ip=ip)
        return cart_item

    def resolve_wishlists(root, info, token):
        wishlist_item = Wishlist.objects.select_related("user")
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
        user = ExtendUser.objects.get(email=email)
        name = user.full_name
        if name:
            wishlist_item = wishlist_item.filter(Q(user_id__full_name__icontains=name) | Q(user_id__full_name__iexact=name)).distinct()
        return wishlist_item
    
    def resolve_products(root, info, search=None, keyword=None, rating=None):
        if search:
            filter = (
                Q(product_title__icontains=search) |
                Q(color__iexact=search) |
                Q(brand__iexact=search) |
                Q(gender__iexact=search) |
                Q(category__name__icontains=search) |
                Q(subcategory__name__icontains=search) |
                Q(short_description__icontains=search) |
                Q(options__price__icontains=search)
            )

            return Product.objects.filter(filter)
            
        if rating:
            rate = rating
            products_included = []
            while rate <= 5:
                products = Product.objects.filter(product_rating__rating__exact=rate)
                for product in products:
                    products_included.append(product)
                rate += 1
            return products_included

        if keyword:
            filter = (
                Q(keyword__overlap=keyword)
            )

            return Product.objects.filter(filter)
        
        return Product.objects.all()
    
    def resolve_review(root, info, review_id):
        review = Rating.objects.get(id=review_id)
        
        return review
    
    def resolve_billing_address(root, info, address_id):
        billing_address = Billing.objects.get(id=address_id)

        return billing_address

    def resolve_pickup_location(root, info, location_id):
        location = Pickups.objects.get(id=location_id)

        return location