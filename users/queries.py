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
    category_by_id = graphene.Field(CategoryType, id=graphene.Int(required=True))
    products = graphene.relay.Node.Field(ProductType)
    all_products = DjangoFilterConnectionField(ProductType)
    subcribers = DjangoListField(NewsletterType)
    carts = graphene.List(CartType, name=graphene.String())
    wishlists = graphene.List(WishlistType, name=graphene.String())

    def resolve_user_data(root, info, token):
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
        return ExtendUser.objects.get(email=email)

    def resolve_seller_data(root, info, token):
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
        c_user = ExtendUser.objects.get(email=email)
        userid = c_user.id
        return SellerProfile.objects.get(user=userid)

    def resolve_category_by_id(root, info, id):
        return Category.objects.get(pk=id)

    def resolve_carts(root, info, name=False):
        cart_item = Cart.objects.select_related("user", "product").filter(user_id=info.context.user.id)

        if name:
            cart_item = cart_item.filter(Q(product__name__icontains=name) | Q(product__name__iexact=name)).distinct()
        return cart_item

    def resolve_wishlists(root, info, name=False):
        wishlist_item = Cart.objects.select_related("user", "product").filter(user_id=info.context.user.id)

        if name:
            wishlist_item = wishlist_item.filter(Q(product__name__icontains=name) | Q(product__name__iexact=name)).distinct()
        return wishlist_item
