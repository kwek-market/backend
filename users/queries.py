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


class Query(UserQuery, MeQuery, graphene.ObjectType):
    user_data = graphene.Field(UserType, token=graphene.String())
    seller_data = graphene.Field(SellerProfileType, token=graphene.String())

    categories = DjangoListField(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.Int(required=True))
    product = graphene.relay.Node.Field(ProductType)
    products = graphene.List(ProductType, search=graphene.String(), keyword=graphene.List(graphene.String))
    subcribers = DjangoListField(NewsletterType)
    carts = graphene.List(CartType, token=graphene.String(), ip=graphene.String())
    wishlists = graphene.List(WishlistType, name=graphene.String(), ip=graphene.String())

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

    def resolve_carts(root, info, token=None, ip=None):
        if token is not None:
            email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
            user = ExtendUser.objects.get(email=email)
            if user.exists():
                cart_item = Cart.objects.select_related("user", "product").filter(user=user)
        if ip is not None:
            cart_item = Cart.objects.select_related("user", "product").filter(ip=ip)
        return cart_item

    def resolve_wishlists(root, info, name=False):
        wishlist_item = Wishlist.objects.select_related("user", "products").filter(user_id=info.context.user.id)

        if name:
            wishlist_item = wishlist_item.filter(Q(user__name__icontains=name) | Q(user__name__iexact=name)).distinct()
        return wishlist_item
    
    def resolve_products(root, info, search=None, keyword=None):
        if search:
            filter = (
                Q(product_title__icontains=search) |
                Q(color__iexact=search) |
                Q(brand__iexact=search) |
                Q(gender__iexact=search) |
                Q(category__name__icontains=search) |
                Q(short_description__icontains=search)
            )

            return Product.objects.filter(filter)
        
        if keyword:
            filter = (
                Q(keyword__overlap=keyword)
            )

            return Product.objects.filter(filter)
        
        return Product.objects.all()