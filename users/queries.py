import graphene
import uuid
import random
from graphene_django import DjangoListField
from graphql_auth.schema import UserQuery, MeQuery
from market.post_offices import get_paginator
from notifications.models import Message, Notification
from graphql import GraphQLError
from django.db.models import Sum
from datetime import datetime

from notifications.object_types import MessageType
from wallet.models import Invoice, StoreDetail, Wallet, WalletTransaction
from wallet.object_types import InvoiceType, StoreDetailType, WalletTransactionType, WalletType
from .model_object_type import UserType, SellerProfileType
from market.object_types import *
from users.models import SellerCustomer, SellerProfile
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
    products = graphene.Field(ProductPaginatedType, page=graphene.Int(),page_size=graphene.Int(), search=graphene.String(), rating=graphene.Int(), keyword=graphene.List(graphene.String), clicks=graphene.String(), sales=graphene.String())
    subcribers = DjangoListField(NewsletterType)
    contact_us = DjangoListField(ContactMessageType)
    coupons = DjangoListField(CouponType)
    user_cart = graphene.List(CartItemType, token=graphene.String(), ip=graphene.String())
    wishlists = graphene.List(WishlistItemType, token=graphene.String(required=True))
    reviews = DjangoListField(RatingType)
    review = graphene.Field(RatingType, review_id=graphene.String(required=True))
    billing_addresses = DjangoListField(BillingType)
    user_billing_addresses = graphene.Field(BillingType, token=graphene.String(required=True))
    billing_address = graphene.Field(PickupType, address_id=graphene.String(required=True))
    pickup_locations = DjangoListField(PickupType)
    pickup_location = graphene.Field(PickupType, location_id=graphene.String(required=True))
    orders = graphene.List(OrderType, token=graphene.String(required=True))
    rating_sort = graphene.Field(ProductType)
    user_notifications = graphene.List(MessageType, token=graphene.String(required=True))
    get_seller_products = graphene.List(ProductType, token=graphene.String(required=True), this_month=graphene.Boolean(), rating=graphene.Boolean(), price=graphene.String(), popular=graphene.Boolean(), recent=graphene.Boolean())
    get_seller_review = graphene.List(RatingType, token=graphene.String(required=True))
    get_seller_promoted_products = graphene.List(ProductType, token=graphene.String(required=True))
    get_seller_orders = graphene.JSONString(token=graphene.String(required=True), this_month=graphene.Boolean())
    get_seller_store_detail = graphene.List(StoreDetailType, token=graphene.String(required=True))
    get_seller_invoices = graphene.List(InvoiceType, token=graphene.String(required=True))
    get_seller_wallet = graphene.List(WalletType, token=graphene.String(required=True))
    get_seller_wallet_transactions = graphene.List(WalletTransactionType, token=graphene.String(required=True))
    # locations = graphene.List()
    get_seller_successful_sales = graphene.List(SalesType, token=graphene.String(required=True))
    get_seller_product_quality = graphene.JSONString(token=graphene.String(required=True))
    get_seller_delivery_rate = graphene.JSONString(token=graphene.String(required=True))
    get_seller_days_selling = graphene.JSONString(token=graphene.String(required=True))
    get_seller_product_promotion_reach = graphene.JSONString(token=graphene.String(required=True), this_month=graphene.Boolean())
    get_seller_product_promotion_link_clicks = graphene.JSONString(token=graphene.String(required=True), this_month=graphene.Boolean())
    get_seller_product_promotion_amount = graphene.JSONString(token=graphene.String(required=True), this_month=graphene.Boolean())
    get_seller_customers = graphene.JSONString(token=graphene.String(required=True), this_month=graphene.Boolean())
    get_seller_sales_earnings = graphene.JSONString(token=graphene.String(required=True), this_month=graphene.Boolean())
    get_seller_revenue_chart_data = graphene.JSONString(token=graphene.String(required=True))

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
    
    def resolve_get_seller_products(root, info, token, this_month=False, rating=False, popular=False, recent=False, price=None):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if SellerProfile.objects.filter(user=user).exists():
                if rating:
                    rate = rating
                    products_included = []
                    # if rating > 5:
                    #     clicks = Product.objects.all()
                    #     sort = sorted(clicks, key=attrgetter("clicks"), reverse=True)
                    while rate <= 5:
                        products = Product.objects.filter(product_rating__rating__exact=rate, user=user)
                        for product in products:
                            products_included.append(product)
                        rate += 1
                    return {
                        "Seller products": products_included
                    }
                elif popular:
                    clicks = Product.objects.filter(user=user)
                    sort = sorted(clicks, key=attrgetter("clicks"), reverse=True)
                    return sort
                elif recent:
                    sort = Product.objects.filter(user=user).order_by("-date_created")
                    return sort
                elif price and price == "up":
                    sort = Product.objects.filter(user=user).order_by("options__price")
                    return sort
                elif price and price == "down":
                    sort = Product.objects.filter(user=user).order_by("-options__price")
                    return sort
                elif this_month:
                    this_month = Product.objects.filter(date_created__month=datetime.now().month, date_created__year=datetime.now().year, user=user)
                    return this_month
                else:
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
    
    def resolve_products(root, info, page, page_size=50, search=None, keyword=None, rating=None, clicks=None, sales=None):
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
            qs = Product.objects.filter(filter).distinct()
            return get_paginator(qs, page_size, page, ProductPaginatedType)
            products = Product.objects.filter(filter).distinct()
            return products
            # for product in products:
            #     filtered_products.append(products)
            
        if rating:
            rate = rating
            products_included = []
            while rate <= 5:
                products = Product.objects.filter(product_rating__rating__exact=rate)
                for product in products:
                    products_included.append(product)
                rate += 1
            
            qs = products_included
            return get_paginator(qs, page_size, page, ProductPaginatedType)

        if keyword:
            filter = (
                Q(keyword__overlap=keyword)
            )

            products = Product.objects.filter(filter)

            qs = products
            return get_paginator(qs, page_size, page, ProductPaginatedType)
            return products
            # filtered_products.append(products)
        
        if clicks:
            clicks = Product.objects.all()
            sort = sorted(clicks, key=attrgetter("clicks"), reverse=True)
            
            qs = sort
            return get_paginator(qs, page_size, page, ProductPaginatedType)
        
        if sales:
            sales = Product.objects.all()
            sort = sorted(sales, key=attrgetter("sales"), reverse=True)

            qs = sort
            return get_paginator(qs, page_size, page, ProductPaginatedType)

        qs = Product.objects.all()
        return get_paginator(qs, page_size, page, ProductPaginatedType)

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
        if user.is_seller:
            review = Rating.objects.filter(product__user=user)
            return review
        else:
            raise GraphQLError("Not a seller")
    
    def resolve_get_seller_promoted_products(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            promoted_products = Product.objects.filter(user=user, promoted=True)
            return promoted_products
        else:
            raise GraphQLError("Not a seller")

    
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
            detail = StoreDetail.objects.filter(user=user)
            return detail
        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_invoices(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if StoreDetail.objects.filter(user=user).exists():
                store = StoreDetail.objects.get(user=user)
                invoice = Invoice.objects.filter(store=store)
                return invoice
            else:
                raise GraphQLError("Store detail invalid")

        else:
            raise GraphQLError("Not a seller")
    
    def resolve_get_seller_wallet(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            wallet= Wallet.objects.filter(owner=user)
            return wallet
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


    def resolve_get_seller_successful_sales(root, info, token, this_month=False):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if this_month:
                this_month = Sales.objects.filter(date__month=datetime.now().month, date__year=datetime.now().year, product__user=user).aggregate(Sum("amount"))
                return this_month["amount__sum"]       
            else:
                sales = Sales.objects.filter(product__user=user).aggregate(Sum("amount"))
                return sales["amount__sum"]
        else:
            raise GraphQLError("Not a seller")
    
    def resolve_get_seller_sales_earnings(root, info, token, this_month=False):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if this_month:
                sales_earnings = Sales.objects.filter(date__month=datetime.now().month, date__year=datetime.now().year, product__user=user).aggregate(Sum("amount"))
            else:
                sales_earnings = Sales.objects.filter(product__user=user).aggregate(Sum("amount"))
            if sales_earnings["amount__sum"]:
                kwek_charges = sales_earnings["amount__sum"] * SellerProfile.objects.get(user=user).kwek_charges
                return sales_earnings - kwek_charges
            else:
                return 0
        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_product_quality(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            rating_sum = Rating.objects.filter(product__user=user).aggregate(Sum("rating"))
            rating_total_sum = Rating.objects.filter(product__user=user).count() * 5
            if rating_sum["rating__sum"]:
                rating_percent = (rating_sum["rating__sum"]/rating_total_sum) * 100
                return rating_percent
            else:
                return 0
        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_delivery_rate(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            all_orders = 0
            successful_orders = 0
            orders = Order.objects.all()
            for order in orders:
                for id in order.cart_items:
                    item = CartItem.objects.get(id=id)
                    if item.product.user == user:
                        all_orders += 1
                        if order.delivery_status == "delivered":
                            successful_orders += 1
            if all_orders > 0 and successful_orders > 0:
                delivery_rate_percent = (successful_orders/all_orders) * 100
            else:
                delivery_rate_percent = 0
            return delivery_rate_percent
        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_days_selling(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            days = SellerProfile.objects.get(user=user).since

            return days
        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_product_promotion_reach(root, info, token, this_month=False):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if this_month:
                reach = ProductPromotion.objects.filter(date__month=datetime.now().month, date__year=datetime.now().year, product__user=user).aggregate(Sum("reach"))
            else:
                reach = ProductPromotion.objects.filter(product__user=user).aggregate(Sum("reach"))
            if reach["reach__sum"]:
                return reach["reach__sum"]
            else:
                return 0
        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_product_promotion_link_clicks(root, info, token, this_month=False):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if this_month:
                link_clicks = ProductPromotion.objects.filter(date__month=datetime.now().month, date__year=datetime.now().year, product__user=user).aggregate(Sum("link_clicks"))
            else:
                link_clicks = ProductPromotion.objects.filter(product__user=user).aggregate(Sum("link_clicks"))
            if link_clicks["link_clicks__sum"]:
                return link_clicks["link_clicks__sum"]
            else:
                return 0
        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_product_promotion_amount(root, info, token, this_month=True):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if this_month:
                amount = ProductPromotion.objects.filter(date__month=datetime.now().month, date__year=datetime.now().year, product__user=user).aggregate(Sum("amount"))
            else:
                amount = ProductPromotion.objects.filter(product__user=user).aggregate(Sum("amount"))
            if amount["amount__sum"]:
                return amount["amount__sum"]
            else:
                return 0
        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_customer(root, info, token, this_month=False):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if this_month:
                customer_id = SellerCustomer.objects.filter(date__month=datetime.now().month, date__year=datetime.now().year, seller=user).customer_id
            else:
                customer_id = SellerCustomer.objects.get(seller=user).customer_id
            return len(customer_id)
        else:
            raise GraphQLError("Not a seller")
    
    def resolve_get_seller_orders(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        orders = Order.objects.all()
        seller_orders = {}
        charge = SellerProfile.objects.get(user=user).kwek_charges
        for order in orders:
            cart_items = order.cart_items
            for id in cart_items:
                id = uuid.UUID(id)
                item = CartItem.objects.get(id=id)
                if item.product.user == user:
                    seller_orders[order.order_id] = {
                            "created": str(order.date_created),
                            "customer_id": str(order.user.id),
                            "total": int(item.price),
                            "profit": int(item.price) - (int(item.price) * charge),
                            "paid": order.paid,
                            "status": order.progress.progress
                        }

        return seller_orders
    
    def resolve_get_seller_revenue_chart_data(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            data ={}
            for i in range(1, datetime.now().month):
                sales = Sales.objects.filter(date__month=i, date__year=datetime.now().year, product__user=user).aggregate(Sum("amount"))
                if sales["amount__sum"]:
                    kwek_charges = sales["amount__sum"] * SellerProfile.objects.get(user=user).kwek_charges
                    sales_earnings = sales["amount__sum"] - kwek_charges
                    data[i] = sales_earnings
            return data
        else:
            raise GraphQLError("Not a seller")