import this
from typing_extensions import Required
import graphene
import uuid
import random, math
from graphene_django import DjangoListField
from graphql_auth.schema import UserQuery, MeQuery
from market.post_offices import get_paginator
from notifications.models import Message, Notification
from graphql import GraphQLError
from django.db.models import Sum
from datetime import datetime
from django.db.models import F, Count, Subquery, OuterRef

from notifications.object_types import MessageType
from wallet.models import Invoice, StoreDetail, Wallet, WalletTransaction
from wallet.object_types import (
    InvoiceType,
    StoreDetailType,
    WalletTransactionType,
    WalletType,
)
from .model_object_type import UserType, SellerProfileType
from market.object_types import *
from users.models import SellerCustomer, ExtendUser, SellerProfile
from users.validate import authenticate_user
from django.db.models import Q
from bill.object_types import *
from operator import attrgetter


class Query(UserQuery, MeQuery, graphene.ObjectType):
    billing_address = graphene.Field(
        PickupType, address_id=graphene.String(required=True)
    )
    billing_addresses = DjangoListField(BillingType)
    categories = graphene.List(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.String(required=True))
    contact_us = DjangoListField(ContactMessageType)
    coupons = DjangoListField(CouponType)
    cartitem = graphene.Field(CartItemType, id=graphene.String(required=True))
    deals_of_the_day = graphene.List(ProductType)
    get_seller_products = graphene.Field(
        ProductPaginatedType,
        token=graphene.String(required=True),
        page_size=graphene.Int(),
        page=graphene.Int(),
        this_month=graphene.Boolean(),
        rating=graphene.Int(),
        price=graphene.String(),
        popular=graphene.Boolean(),
        recent=graphene.Boolean(),
    )
    get_seller_review = graphene.Field(RatingPaginatedType, page=graphene.Int(), page_size=graphene.Int(), token=graphene.String(required=True))
    get_seller_promoted_products = graphene.List(
        ProductType, token=graphene.String(required=True)
    )
    get_seller_orders = graphene.List(
        GetSellerOrdersType,
        token=graphene.String(required=True),
        this_month=graphene.Boolean(),
    )
    get_seller_store_detail = graphene.List(
        StoreDetailType, token=graphene.String(required=True)
    )
    get_seller_invoices = graphene.List(
        InvoiceType, token=graphene.String(required=True)
    )
    get_seller_invoice = graphene.Field(
        InvoiceType,
        invoice_id=graphene.String(required=True),
        token=graphene.String(required=True),
    )
    get_seller_wallet = graphene.List(WalletType, token=graphene.String(required=True))
    get_seller_wallet_transactions = graphene.List(
        WalletTransactionType, token=graphene.String(required=True)
    )
    # locations = graphene.List()
    get_seller_successful_sales = graphene.JSONString(
        token=graphene.String(required=True), this_month=graphene.Boolean()
    )
    get_seller_product_quality = graphene.JSONString(
        token=graphene.String(required=True)
    )
    get_seller_delivery_rate = graphene.JSONString(token=graphene.String(required=True))
    get_seller_days_selling = graphene.JSONString(token=graphene.String(required=True))
    get_seller_product_promotion_reach = graphene.JSONString(
        token=graphene.String(required=True), this_month=graphene.Boolean()
    )
    get_seller_product_promotion_link_clicks = graphene.JSONString(
        token=graphene.String(required=True), this_month=graphene.Boolean()
    )
    get_seller_product_promotion_amount = graphene.JSONString(
        token=graphene.String(required=True), this_month=graphene.Boolean()
    )
    get_seller_customers = graphene.JSONString(
        token=graphene.String(required=True), this_month=graphene.Boolean()
    )
    get_seller_sales_earnings = graphene.JSONString(
        token=graphene.String(required=True), this_month=graphene.Boolean()
    )
    get_seller_revenue_chart_data = graphene.JSONString(
        token=graphene.String(required=True)
    )
    least_subcategories = graphene.List(CategoryType)
    orders = graphene.List(OrderType, token=graphene.String(required=True))
    order = graphene.Field(
        OrderType,
        token=graphene.String(required=True),
        id=graphene.String(required=True),
    )
    pickup_locations = DjangoListField(PickupType)
    pickup_location = graphene.Field(
        PickupType, location_id=graphene.String(required=True)
    )
    product = graphene.Field(ProductType, id=graphene.String(required=True))
    products = graphene.Field(
        ProductPaginatedType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        search=graphene.String(),
        rating=graphene.Int(),
        keyword=graphene.List(graphene.String),
        clicks=graphene.String(),
        sales=graphene.String(),
    )
    rating_sort = graphene.Field(ProductType)
    reviews = DjangoListField(RatingType, page=graphene.Int(), page_size=graphene.Int(), product_id=graphene.String(required=False))
    review = graphene.Field(RatingPaginatedType, review_id=graphene.String(required=True))
    seller_data = graphene.Field(SellerProfileType, token=graphene.String())
    subcategories = graphene.List(CategoryType)
    subcribers = DjangoListField(NewsletterType)
    user_data = graphene.Field(UserType, token=graphene.String())
    user_cart = graphene.List(
        CartItemType, token=graphene.String(), ip=graphene.String()
    )
    user_billing_addresses = graphene.Field(
        BillingType, token=graphene.String(required=True)
    )
    user_notifications = graphene.List(
        MessageType, token=graphene.String(required=True)
    )
    wishlists = graphene.List(WishlistItemType, token=graphene.String(required=True))

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

    def resolve_categories(root, info):
        cat_list = Category.objects.filter(parent=None)
        return cat_list

    def resolve_category(root, info, id):
        return Category.objects.get(id=id)

    def resolve_contact_us(root, info):
        return ContactMessage.objects.all().order_by("-sent_at")

    def resolve_cartitem(root, info, id):
        item = CartItem.objects.get(id=id)
        return item

    def resolve_deals_of_the_day(root, info):
        return Product.objects.filter(promoted=True)

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

    def resolve_get_seller_products(
        root,
        info,
        token,
        page_size=10,
        page=1,
        this_month=False,
        rating=False,
        popular=False,
        recent=False,
        price=None,
    ):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if SellerProfile.objects.filter(user=user).exists():
                if rating:
                    prods = Product.objects.annotate(rate = Sum('product_rating__rating')/Count('product_rating__rating')).filter(user=user,rate__lte=rating).order_by('-rate')
                elif popular:
                    prods = Product.objects.filter(user=user).order_by("-clicks")
                elif recent:
                    prods = Product.objects.filter(user=user).order_by("-date_created")
                elif price and price == "up":
                    prods = Product.objects.filter(user=user).order_by("options__price")
                elif price and price == "down":
                    prods = Product.objects.filter(user=user).order_by(
                        "-options__price"
                    )
                elif this_month:
                    prods = Product.objects.filter(
                        date_created__month=datetime.now().month,
                        date_created__year=datetime.now().year,
                        user=user,
                    )
                else:
                    prods = Product.objects.filter(user=user).order_by('?')

                return get_paginator(prods, page_size, page, ProductPaginatedType)

    def resolve_category(root, info, id):
        return Category.objects.get(id=id)

    def resolve_categories(root, info):
        cat_list = Category.objects.filter(parent=None)

        return cat_list

    def resolve_subcategories(root, info):
        categories = Category.objects.all()
        cat_list = []

        for category in categories:
            if category.parent:
                cat_list.append(category)
        return cat_list

    def resolve_least_subcategories(root, info):
        cat_list = Category.objects.filter(child=None)
        return cat_list

    def resolve_user_cart(root, info, token=None, ip=None):
        if token is not None:
            auth = authenticate_user(token)
            if not auth["status"]:
                raise GraphQLError(auth["message"])
            user = auth["user"]
            if user:
                cart = Cart.objects.get(user=user)
                try:
                    if cart:
                        cart_items = CartItem.objects.filter(cart=cart, ordered=False)
                    else:
                        cart_items = []
                except Exception as e:
                    cart_items = []

                return cart_items
        elif ip is not None:
            try:
                cart = Cart.objects.get(ip=ip)
                cart_items = CartItem.objects.filter(cart=cart)
            except Exception as e:
                cart_items = []

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

    def resolve_products(
        root,
        info,
        page,
        page_size=50,
        search=None,
        keyword=None,
        rating=None,
        clicks=None,
        sales=None,
    ):
        if search:
            filter = (
                Q(product_title__icontains=search)
                | Q(color__iexact=search)
                | Q(brand__iexact=search)
                | Q(gender__iexact=search)
                | Q(category__name__icontains=search)
                | Q(subcategory__name__icontains=search)
                | Q(short_description__icontains=search)
                | Q(options__price__icontains=search)
            )
            return get_paginator(Product.objects.filter(filter).distinct(), page_size, page, ProductPaginatedType)

        if rating:
            return get_paginator(Product.objects.annotate(rate = Sum('product_rating__rating')/Count('product_rating__rating')).filter(rate__lte=rating).order_by('-rate'), page_size, page, ProductPaginatedType)

        if keyword:
            return get_paginator(Product.objects.filter(Q(keyword__overlap=keyword)), page_size, page, ProductPaginatedType)

        if clicks:
            return get_paginator(Product.objects.all().order_by('-clicks'), page_size, page, ProductPaginatedType)

        if sales:
            return get_paginator(Product.objects.all().order_by('-sales'), page_size, page, ProductPaginatedType)

        return get_paginator(Product.objects.all().order_by('?'), page_size, page, ProductPaginatedType)

    def resolve_review(root, info, review_id):
        review = Rating.objects.get(id=review_id)

    def resolve_reviews(root, info,page, page_size, product_id=None):
        if product_id:
            product = Product.objects.get(id=product_id)
            reviews = Rating.objects.filter(product=product)
        else:
            reviews = Rating.objects.all().order_by("rated_at")

        return get_paginator(reviews, page_size, page, RatingPaginatedType)

    def resolve_get_seller_review(root, info, page, page_size, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            reviews = Rating.objects.filter(product__user=user)
            return get_paginator(reviews, page_size, page, RatingPaginatedType)
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

    def resolve_order(root, info, token, id):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        user_order = Order.objects.get(user=user, id=id)
        return user_order

    def resolve_user_notifications(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        notification = Notification.objects.get(user=user)
        messages = Message.objects.filter(notification=notification).order_by(
            "-created_at"
        )

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

    def resolve_get_seller_invoice(root, info, invoice_id, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if StoreDetail.objects.filter(user=user).exists():
                store = StoreDetail.objects.get(user=user)
                invoice = Invoice.objects.get(store=store, id=invoice_id)
                return invoice
            else:
                raise GraphQLError("Store details invalid")

        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_wallet(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            wallet = Wallet.objects.filter(owner=user)
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
                # this_month = Sales.objects.filter(date__month=datetime.now().month, date__year=datetime.now().year, product__user=user).aggregate(Sum("amount"))
                # return this_month["amount__sum"]
                this_month = Sales.objects.filter(
                    date__month=datetime.now().month,
                    date__year=datetime.now().year,
                    product__user=user,
                ).count()
                return this_month
            else:
                # sales = Sales.objects.filter(product__user=user).aggregate(Sum("amount"))
                # return sales["amount__sum"]
                sales = Sales.objects.filter(product__user=user).count()
                return sales
        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_sales_earnings(root, info, token, this_month=False):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if this_month:
                sales_earnings = Sales.objects.filter(
                    date__month=datetime.now().month,
                    date__year=datetime.now().year,
                    product__user=user,
                ).aggregate(Sum("amount"))
            else:
                sales_earnings = Sales.objects.filter(product__user=user).aggregate(
                    Sum("amount")
                )
            if sales_earnings["amount__sum"]:
                print("amount", sales_earnings)
                kwek_charges = (
                    sales_earnings["amount__sum"]
                    * SellerProfile.objects.get(user=user).kwek_charges
                )
                return sales_earnings["amount__sum"] - kwek_charges
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
            rating_sum = Rating.objects.filter(product__user=user).aggregate(
                Sum("rating")
            )
            rating_total_sum = Rating.objects.filter(product__user=user).count() * 5
            if rating_sum["rating__sum"]:
                rating_percent = math.ceil((rating_sum["rating__sum"] / rating_total_sum) * 100)
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
            orders = Order.objects.filter(cart_items__product__user=user)
            delivered_orders = Order.objects.filter(
                cart_items__product__user=user, delivery_status="delivered"
            )
            all_orders, successful_orders = orders.count(), delivered_orders.count()
            if all_orders > 0 and successful_orders > 0:
                delivery_rate_percent = math.ceil((successful_orders / all_orders) * 100)
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
                reach = ProductPromotion.objects.filter(
                    date__month=datetime.now().month,
                    date__year=datetime.now().year,
                    product__user=user,
                ).aggregate(Sum("reach"))
            else:
                reach = ProductPromotion.objects.filter(product__user=user).aggregate(
                    Sum("reach")
                )
            if reach["reach__sum"]:
                return reach["reach__sum"]
            else:
                return 0
        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_product_promotion_link_clicks(
        root, info, token, this_month=False
    ):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if this_month:
                link_clicks = ProductPromotion.objects.filter(
                    date__month=datetime.now().month,
                    date__year=datetime.now().year,
                    product__user=user,
                ).aggregate(Sum("link_clicks"))
            else:
                link_clicks = ProductPromotion.objects.filter(
                    product__user=user
                ).aggregate(Sum("link_clicks"))
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
                amount = ProductPromotion.objects.filter(
                    date__month=datetime.now().month,
                    date__year=datetime.now().year,
                    product__user=user,
                ).aggregate(Sum("amount"))
            else:
                amount = ProductPromotion.objects.filter(product__user=user).aggregate(
                    Sum("amount")
                )
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
                customer_id = SellerCustomer.objects.filter(
                    date__month=datetime.now().month,
                    date__year=datetime.now().year,
                    seller=user,
                ).customer_id
            else:
                customer_id = SellerCustomer.objects.get(seller=user).customer_id
            return len(customer_id)
        else:
            raise GraphQLError("Not a seller")

    def resolve_get_seller_orders(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user, seller_orders = auth["user"], []
        charge = SellerProfile.objects.get(user=user).kwek_charges
        orders = Order.objects.filter(cart_items__product__user=user)
        orders_values = orders.values(
            "order_id",
            "date_created",
            "user__id",
            "paid",
            "cart_items__price",
            "progress__progress",
        )
        for i in orders_values:
            seller_orders.append(
                GetSellerOrdersType(
                    order=Order.objects.get(order_id=i["order_id"]),
                    created=str(i["date_created"]),
                    customer=ExtendUser.objects.get(id=i["user__id"]),
                    total=int(i["cart_items__price"]),
                    profit=int(i["cart_items__price"])
                    - (int(i["cart_items__price"]) * charge),
                    paid=i["paid"],
                    status=i["cart_items__price"],
                )
            )
        return seller_orders

    def resolve_get_seller_revenue_chart_data(root, info, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            data = {}
            for i in range(1, 13):
                sales = Sales.objects.filter(
                    date__month=i, date__year=datetime.now().year, product__user=user
                ).aggregate(Sum("amount"))
                if sales["amount__sum"]:
                    kwek_charges = (
                        sales["amount__sum"]
                        * SellerProfile.objects.get(user=user).kwek_charges
                    )
                    sales_earnings = sales["amount__sum"] - kwek_charges
                    data[i] = sales_earnings
                else:
                    data[i] = 0
            return data
        else:
            raise GraphQLError("Not a seller")
