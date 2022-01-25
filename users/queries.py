import graphene
import jwt
from graphene_django import DjangoListField
from graphene_django.filter import DjangoFilterConnectionField
from graphql_auth.schema import UserQuery, MeQuery
from django.conf import settings
from notifications.models import Message, Notification
from graphql import GraphQLError

from notifications.object_types import MessageType
from wallet.models import Invoice, StoreDetail, Wallet, WalletTransaction
from wallet.object_types import InvoiceType, StoreDetailType, WalletTransactionType, WalletType
from .model_object_type import UserType, SellerProfileType
from market.object_types import *
from users.models import ExtendUser, SellerProfile
from users.validate import authenticate_user
from django.db.models import Q
from bill.object_types import *
from operator import attrgetter


class Query(UserQuery, MeQuery, graphene.ObjectType):
    user_data = graphene.Field(UserType, token=graphene.String())
    seller_data = graphene.Field(SellerProfileType, token=graphene.String())
    categories = graphene.List(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.String(required=True))
    subcategories = graphene.List(CategoryType)
    least_subcategories = graphene.List(CategoryType)
    product = graphene.Field(ProductType, id=graphene.String(required=True))
    seller_products = graphene.List(ProductType, token=graphene.String(required=True))
    products = graphene.List(ProductType, search=graphene.String(), rating=graphene.Int(), keyword=graphene.List(graphene.String), clicks=graphene.String(), sales=graphene.String())
    subcribers = DjangoListField(NewsletterType)
    contact_us = DjangoListField(ContactMessageType)
    user_cart = graphene.List(CartItemType, token=graphene.String(), ip=graphene.String())
    wishlists = graphene.List(WishlistItemType, token=graphene.String(required=True))
    reviews = DjangoListField(RatingType)
    review = graphene.Field(RatingType, review_id=graphene.String(required=True))
    billing_addresses = DjangoListField(BillingType)
    user_billing_addresses = graphene.Field(BillingType, token=graphene.String(required=True))
    billing_address = graphene.Field(PickupType, address_id=graphene.String(required=True))
    pickup_locations = DjangoListField(PickupType)
    pickup_location = graphene.Field(PickupType, location_id=graphene.String(required=True))
    orders = graphene.Field(OrderType, token=graphene.String(required=True))
    rating_sort = graphene.Field(ProductType)
    user_notifications = graphene.List(MessageType, token=graphene.String(required=True))
    get_seller_review = graphene.Field(RatingType, token=graphene.String(required=True))
    get_seller_promoted_products = graphene.Field(RatingType, token=graphene.String(required=True))
    # get_seller_orders = graphene.Field(OrderType, token=graphene.String(required=True))
    get_seller_store_detail = graphene.List(StoreDetailType, token=graphene.String(required=True))
    get_seller_invoices = graphene.List(InvoiceType, token=graphene.String())
    get_seller_wallet = graphene.List(WalletType, token=graphene.String(required=True))
    get_seller_wallet_transactions = graphene.List(WalletTransactionType, token=graphene.String(required=True))

    def resolve_user_data(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        return auth["user"]

    def resolve_seller_data(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        return SellerProfile.objects.get(user=auth["user"].id)
    
    def resolve_seller_products(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if SellerProfile.objects.filter(user=user).exists():
                seller_products = Product.objects.filter(user=user)

                return seller_products
    
    def resolve_category(root, info, id):
        return Category.objects.get(id=id)

    def resolve_categories(root, info):
        cat_list=Category.objects.filter(parent=None)

        return cat_list

    def resolve_subcategories(root, info):
        categories = Category.objects.all()
        cat_list=[]

        for category in categories:
            if category.parent:
                cat_list.append(category)
        return cat_list
    
    def resolve_least_subcategories(root, info):
        cat_list=Category.objects.filter(child=None)
        return cat_list

    def resolve_user_cart(root, info, token=None, ip=None):
        if token is not None:
            auth = authenticate_user(token)
            if not auth["status"]:
                raise GraphQLError(auth["message"])
            user = auth["user"]
            if user:
                cart = Cart.objects.get(user=user)
                if cart:
                    cart_items=CartItem.objects.filter(cart=cart)
                else:
                    cart_items=[]
                return cart_items
        elif ip is not None:
            cart = Cart.objects.get(ip=ip)
            cart_items = CartItem.objects.filter(cart=cart)
            return cart_items

    def resolve_wishlists(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            wishlist = Wishlist.objects.get(user=user)
            wishlist_item = WishListItem.objects.filter(wishlist=wishlist)
            return wishlist_item
    
    def resolve_product(root, info, id):
        product = Product.objects.get(id=id)

        return product
    
    def resolve_products(root, info, search=None, keyword=None, rating=None, clicks=None, sales=None):
        # if search or keyword or rating or clicks or sales:
        #     filtered_products = []
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

            products = Product.objects.filter(filter).distinct()
            return products
            # for product in products:
            #     filtered_products.append(products)
            
        if rating:
            rate = rating
            products_included = []
            # if rating > 5:
            #     clicks = Product.objects.all()
            #     sort = sorted(clicks, key=attrgetter("clicks"), reverse=True)
            while rate <= 5:
                products = Product.objects.filter(product_rating__rating__exact=rate)
                for product in products:
                    products_included.append(product)
                rate += 1
            return products_included
            # filtered_products.append(products_included)

        if keyword:
            filter = (
                Q(keyword__overlap=keyword)
            )

            products = Product.objects.filter(filter)
            return products
            # filtered_products.append(products)
        
        if clicks:
            clicks = Product.objects.all()
            sort = sorted(clicks, key=attrgetter("clicks"), reverse=True)
            return sort
            # filtered_products.append(sort)
        
        if sales:
            sales = Product.objects.all()
            sort = sorted(sales, key=attrgetter("sales"), reverse=True)
            return sort
            # filtered_products.append(sort)

        # return filtered_products
        # else:
        return Product.objects.all()

    def resolve_contact_us(root, info):
       return ContactMessage.objects.all().order_by('-sent_at')
    
    def resolve_review(root, info, review_id):
        review = Rating.objects.get(id=review_id)
        
        return review
    def resolve_get_seller_review(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]

        review = Rating.objects.filter(product__user__user=user)
        
        return review
    
    def resolve_get_seller_promoted_products(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]

        promoted_products = Product.objects.filter(user=user, promoted=True)
        
        return promoted_products
    
    def resolve_billing_address(root, info, address_id):
        billing_address = Billing.objects.get(id=address_id)

        return billing_address
    def resolve_user_billing_addresses(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        billing_addresses = []
        for address in Billing.objects.all():
            if address.user == user:
                billing_addresses.append(address)
        return billing_addresses

    def resolve_pickup_location(root, info, location_id):
        location = Pickup.objects.get(id=location_id)

        return location
    
    def resolve_orders(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        user_orders = Order.objects.filter(user=user)

        return user_orders
    
    # def resolve_get_seller_orders(root, info, token):
    #     auth = authenticate_user(token)
    #     if not auth["status"]:
    #         raise GraphQLError(auth["message"])
    #     user = auth["user"]
    #     user_orders = Order.objects.filter(user=user)

        return user_orders
    
    def resolve_user_notifications(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        notification = Notification.objects.get(user=user)
        messages = Message.objects.filter(notification=notification)

        return messages

    def resolve_get_seller_store_detail(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            return StoreDetail.objects.get(user=user)
        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_invoices(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            store = StoreDetail.objects.get(user=user)
            invoices = Invoice.objects.filter(store=store)

            return invoices
        else:
            raise GraphQLError("Not a seller")
    
    def resolve_get_seller_wallet(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            return Wallet.objects.get(owner=user)
        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_wallet_transactions(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            wallet = Wallet.objects.get(owner=user)
            transactions = WalletTransaction.objects.filter(wallet=wallet)

            return transactions
        else:
            raise GraphQLError("Not a seller")
