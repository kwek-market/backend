import re
import this
from typing_extensions import Required, Self
import graphene
import uuid
import random, math
from graphene_django import DjangoListField
from graphql_auth.schema import UserQuery, MeQuery
from market.post_offices import get_paginator
from notifications.models import Message, Notification
from graphql import GraphQLError
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from kwek_admin.models import *
from django.db.models import (
    F,
    Count,
    Subquery,
    OuterRef,
    FloatField,
    IntegerField,
    BooleanField,
    TextField,
    ExpressionWrapper,
    Prefetch,
)

from notifications.object_types import MessageType
from kwek_admin.object_types import *
from wallet.models import Invoice, StoreDetail, Wallet, WalletTransaction
from wallet.object_types import (
    InvoiceType,
    StoreDetailType,
    WalletTransactionType,
    WalletType,
    InvoicePaginatedType,
    WalletTransactionPaginatedType,
)
from .model_object_type import UserType, SellerProfileType
from market.object_types import *
from users.models import SellerCustomer, ExtendUser, SellerProfile
from users.validate import authenticate_user
from django.db.models import Q
from bill.object_types import *
from operator import attrgetter


def get_price_range(range):
    try:
        return range[0], range[1]
    except:
        raise GraphQLError("wrong price range data")


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
    deals_of_the_day = graphene.Field(
        ProductPaginatedType,
        page=graphene.Int(),
        page_size=graphene.Int(),
    )
    get_seller_products = graphene.Field(
        ProductPaginatedType,
        token=graphene.String(required=True),
        page=graphene.Int(),
        page_size=graphene.Int(),
        search=graphene.String(),
        sort_by=graphene.String(),
        keyword=graphene.List(graphene.String),
        price_range=graphene.List(graphene.Float),
        rating=graphene.Int(),
        sizes=graphene.List(graphene.String),
        this_month=graphene.Boolean(),
    )
    get_seller_review = graphene.Field(
        RatingPaginatedType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        token=graphene.String(required=True),
        sort_by=graphene.String(),
    )
    get_seller_promoted_products = graphene.List(
        ProductType, token=graphene.String(required=True)
    )
    get_seller_orders = graphene.Field(
        GetSellerOrdersPaginatedType,
        token=graphene.String(required=True),
        page=graphene.Int(),
        page_size=graphene.Int(),
        this_month=graphene.Boolean(),
    )
    get_seller_store_detail = graphene.List(
        StoreDetailType, token=graphene.String(required=True)
    )
    get_seller_invoices = graphene.Field(
        InvoicePaginatedType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        token=graphene.String(required=True),
    )
    get_seller_invoice = graphene.Field(
        InvoiceType,
        invoice_id=graphene.String(required=True),
        token=graphene.String(required=True),
    )

    get_seller_wallet = graphene.List(WalletType, token=graphene.String(required=True))
    get_seller_wallet_transactions = graphene.Field(
        WalletTransactionPaginatedType,
        token=graphene.String(required=True),
        page=graphene.Int(),
        page_size=graphene.Int(),
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
        sort_by=graphene.String(),
        keyword=graphene.List(graphene.String),
        price_range=graphene.List(graphene.Float),
        rating=graphene.Int(),
        sizes=graphene.List(graphene.String),
    )
    rating_sort = graphene.Field(ProductType)
    reviews = graphene.Field(
        RatingPaginatedType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        product_id=graphene.String(required=False),
        sort_by=graphene.String(),
    )
    review = graphene.Field(
        RatingPaginatedType, review_id=graphene.String(required=True)
    )
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
    get_total_orders = graphene.Field(
        GetTotalOrdersType,
        start_date = graphene.String(required=True),
        end_date = graphene.String(required=True),
        token = graphene.String(required=True)

    )
    get_total_sales = graphene.Field(
        GetTotalSalesType,
        start_date=graphene.String(required=True),
        end_date=graphene.String(required=True),
        token=graphene.String(required=True)
    )

    get_average_sales = graphene.Field(
        GetAverageOrderValueType,
        start_date=graphene.String(required=True),
        end_date=graphene.String(required=True),
        token=graphene.String(required=True)
    )
    get_total_active_customers = graphene.Field(
        GetTotalActiveCustomersType,
        start_date=graphene.String(required=True),
        end_date=graphene.String(required=True),
        token=graphene.String(required=True)
    )

    wishlists = graphene.List(WishlistItemType, token=graphene.String(required=True))

    def resolve_billing_address(root, info, address_id):
        return Billing.objects.get(id=address_id)

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
        return Category.objects.filter(parent=None)

    def resolve_category(root, info, id):
        return Category.objects.get(id=id)

    def resolve_contact_us(root, info):
        return ContactMessage.objects.all().order_by("-sent_at")

    def resolve_cartitem(root, info, id):
        return CartItem.objects.get(id=id)

    def resolve_deals_of_the_day(root, info, page=1, page_size=5):
        return get_paginator(
            Product.objects.filter(promoted=True).order_by("?"), page_size, page, ProductPaginatedType
        )

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

    def resolve_category(root, info, id):
        return Category.objects.get(id=id)

    def resolve_categories(root, info):
        return Category.objects.filter(parent=None)

    def resolve_subcategories(root, info):
        categories, cat_list = Category.objects.all(), []
        for category in categories:
            if category.parent:
                cat_list.append(category)
        return cat_list

    def resolve_least_subcategories(root, info):
        return Category.objects.filter(child=None)

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
            return WishListItem.objects.filter(wishlist=Wishlist.objects.get(user=user))

    def resolve_product(root, info, id):
        return Product.objects.get(id=id)

    def resolve_get_seller_products(
        root,
        info,
        token,
        page,
        page_size=50,
        search=None,
        sort_by=None,
        keyword=None,
        price_range=None,
        rating=None,
        sizes=None,
        this_month=False,
    ):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if SellerProfile.objects.filter(user=user).exists():
                prods = Product.objects.filter(user=user).order_by("?")
                search_filter, keyword_filter = Q(), Q()
                price_filter, sizes_filter, this_month_filter = Q(), Q(), Q()
                search_status, price_status, sizes_status = False, False, False
                if this_month:
                    this_month_filter = Q(date_created__month=datetime.now().month) & Q(
                        date_created__year=datetime.now().year
                    )
                if search:
                    search_status = True
                    search_filter = (
                        Q(product_title__icontains=search)
                        | Q(color__iexact=search)
                        | Q(brand__iexact=search)
                        | Q(gender__iexact=search)
                        | Q(category__name__icontains=search)
                        | Q(subcategory__name__icontains=search)
                        | Q(short_description__icontains=search)
                        | Q(options__price__icontains=search)
                    )
                if keyword:
                    keyword_filter = Q(keyword__overlap=keyword)
                if price_range:
                    from_price, to_price = get_price_range(price_range)
                    price_filter = (
                        Q(options__price__gte=from_price)
                        & Q(options__price__lte=to_price)
                    ) | (
                        Q(options__discounted_price__gte=from_price)
                        & Q(options__discounted_price__lte=to_price)
                    )
                    price_status = True

                if sizes:
                    sizes_filter, sizes_status = Q(options__size__in=sizes), True

                if search_status or price_status or sizes_status:
                    prods = prods.filter(
                        search_filter,
                        keyword_filter,
                        price_filter,
                        sizes_filter,
                        this_month_filter,
                    ).distinct()
                else:
                    prods = prods.filter(keyword_filter, this_month_filter)
                if sort_by:
                    if sort_by in [
                        "date_created",
                        "-date_created",
                        "clicks",
                        "-clicks",
                    ]:
                        prods = prods.order_by(sort_by)
                    elif sort_by in ["sales", "-sales"]:
                        sort_key = "{}_count".format(sort_by)
                        prods = prods.annotate(sales_count=Count("sales")).order_by(
                            sort_key
                        )
                    elif sort_by in ["price", "-price"]:
                        v1, v2 = "{}_average".format(
                            sort_by
                        ), "{}_discounted_average".format(sort_by)
                        prods = prods.annotate(
                            price_average=ExpressionWrapper(
                                Sum("options__price") / Count("options__price"),
                                output_field=FloatField(),
                            ),
                            price_discounted_average=ExpressionWrapper(
                                Sum("options__discounted_price")
                                / Count("options__discounted_price"),
                                output_field=FloatField(),
                            ),
                        ).order_by(v1, v2)
                    elif sort_by in ["rating", "-rating"]:
                        sort_key = "rate" if sort_by == "rating" else "-rate"
                        if rating:
                            if rating >= 0:
                                prods = (
                                    prods.annotate(
                                        rate=Sum("product_rating__rating")
                                        / Count("product_rating__rating")
                                    )
                                    .filter(rate__lte=rating)
                                    .order_by(sort_key)
                                )
                            else:
                                prods = (
                                    prods.annotate(
                                        rate=Sum("product_rating__rating")
                                        / Count("product_rating__rating")
                                    )
                                    .filter(rate__gte=abs(rating))
                                    .order_by(sort_key)
                                )
                    else:
                        prods = prods
                return get_paginator(prods, page_size, page, ProductPaginatedType)

    def resolve_products(
        root,
        info,
        page,
        page_size=50,
        search=None,
        sort_by=None,
        keyword=None,
        price_range=None,
        rating=None,
        sizes=None,
    ):
        prods = Product.objects.all().order_by("?")
        search_filter, keyword_filter = Q(), Q()
        price_filter, sizes_filter = Q(), Q()
        search_status, price_status, sizes_status = False, False, False
        if search:
            search_status = True
            search_filter = (
                Q(product_title__icontains=search)
                | Q(color__iexact=search)
                | Q(brand__iexact=search)
                | Q(gender__iexact=search)
                | Q(category__name__icontains=search)
                | Q(subcategory__name__icontains=search)
                | Q(short_description__icontains=search)
                | Q(options__price__icontains=search)
            )
            # prods = prods.filter(search_filter).distinct()
        if keyword:
            keyword_filter = Q(keyword__overlap=keyword)
        if price_range:
            from_price, to_price = get_price_range(price_range)
            price_filter = (
                Q(options__price__gte=from_price) & Q(options__price__lte=to_price)
            ) | (
                Q(options__discounted_price__gte=from_price)
                & Q(options__discounted_price__lte=to_price)
            )
            price_status = True

        if sizes:
            sizes_filter, sizes_status = Q(options__size__in=sizes), True

        if search_status or price_status or sizes_status:
            prods = prods.filter(
                search_filter, keyword_filter, price_filter, sizes_filter
            ).distinct()
        else:
            prods = prods.filter(keyword_filter)

        if sort_by:
            if sort_by in ["date_created", "-date_created", "clicks", "-clicks"]:
                prods = prods.order_by(sort_by)
            elif sort_by in ["sales", "-sales"]:
                sort_key = "{}_count".format(sort_by)
                prods = prods.annotate(sales_count=Count("sales")).order_by(sort_key)
            elif sort_by in ["price", "-price"]:
                v1, v2 = "{}_average".format(sort_by), "{}_discounted_average".format(
                    sort_by
                )
                prods = prods.annotate(
                    price_average=ExpressionWrapper(
                        Sum("options__price") / Count("options__price"),
                        output_field=FloatField(),
                    ),
                    price_discounted_average=ExpressionWrapper(
                        Sum("options__discounted_price")
                        / Count("options__discounted_price"),
                        output_field=FloatField(),
                    ),
                ).order_by(v1, v2)
            elif sort_by in ["rating", "-rating"]:
                sort_key = "rate" if sort_by == "rating" else "-rate"
                if rating:
                    if rating >= 0:
                        prods = (
                            prods.annotate(
                                rate=Sum("product_rating__rating")
                                / Count("product_rating__rating")
                            )
                            .filter(rate__lte=rating)
                            .order_by(sort_key)
                        )
                    else:
                        prods = (
                            prods.annotate(
                                rate=Sum("product_rating__rating")
                                / Count("product_rating__rating")
                            )
                            .filter(rate__gte=abs(rating))
                            .order_by(sort_key)
                        )
            else:
                prods = prods
        return get_paginator(prods, page_size, page, ProductPaginatedType)

    def resolve_review(root, info, review_id):
        review = Rating.objects.get(id=review_id)

    def resolve_reviews(root, info, page, page_size, product_id=None, sort_by=None):
        if product_id:
            reviews = Rating.objects.filter(product=Product.objects.get(id=product_id))
        else:
            reviews = Rating.objects.all()

        if sort_by and sort_by in [
            "date_created",
            "-date_created",
            "rating",
            "-rating",
        ]:
            sort_by = (
                "rated_at"
                if sort_by == "date_created"
                else "-rated_at"
                if sort_by == "-date_created"
                else sort_by
            )
            reviews = reviews.order_by(sort_by)
        else:
            reviews = reviews.order_by("-rated_at")
        return get_paginator(reviews, page_size, page, RatingPaginatedType)

    def resolve_get_seller_review(root, info, page, page_size, token, sort_by=None):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            reviews = Rating.objects.filter(product__user=user)
            if sort_by and sort_by in [
                "date_created",
                "-date_created",
                "rating",
                "-rating",
            ]:
                sort_by = (
                    "rated_at"
                    if sort_by == "date_created"
                    else "-rated_at"
                    if sort_by == "-date_created"
                    else sort_by
                )
                reviews = reviews.order_by(sort_by)
            else:
                reviews = reviews.order_by("-rated_at")
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

    def resolve_get_seller_invoices(root, info, token, page=1, page_size=50):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            if StoreDetail.objects.filter(user=user).exists():
                invoice = Invoice.objects.filter(
                    store=StoreDetail.objects.get(user=user)
                )
                return get_paginator(invoice, page_size, page, InvoicePaginatedType)
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

    def resolve_get_seller_wallet_transactions(root, info, token, page=1, page_size=50):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_seller:
            transactions = WalletTransaction.objects.filter(
                wallet=Wallet.objects.get(owner=user)
            )
            return get_paginator(
                transactions, page_size, page, WalletTransactionPaginatedType
            )
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
                rating_percent = math.ceil(
                    (rating_sum["rating__sum"] / rating_total_sum) * 100
                )
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
                delivery_rate_percent = math.ceil(
                    (successful_orders / all_orders) * 100
                )
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

    def resolve_get_seller_orders(
        root, info, token, page=1, page_size=50, this_month=False
    ):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user, seller_orders, this_month_filter = auth["user"], [], Q()
        if this_month:
            this_month_filter = Q(date_created__month=datetime.now().month) & Q(
                date_created__year=datetime.now().year
            )
        charge = SellerProfile.objects.get(user=user).kwek_charges
        orders = Order.objects.filter(this_month_filter, cart_items__product__user=user)

        orders_values = orders.values(
            "order_id",
            "date_created",
            "user__id",
            "paid",
            "cart_items__price",
            "progress__progress",
        )
        print(orders_values)
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
        return get_paginator(
            seller_orders, page_size, page, GetSellerOrdersPaginatedType
        )

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
        

###################################################################################        #
    def resolve_get_total_orders(root, info, start_date, end_date, token):
        auth = authenticate_user(token)
        if not auth["status"]:
           raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_admin:
            start_datetime = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_datetime = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
            previous_month_start = (start_datetime.replace(day=1) - timedelta(days=1)).replace(day=1)
            previous_month_end = start_datetime - timedelta(days=1)
            prev_month_orders = Order.objects.filter(date_created__range=[previous_month_start, previous_month_end]).count()
            this_month_orders = Order.objects.filter(date_created__range=[start_datetime, end_datetime]).count()
            if prev_month_orders and this_month_orders != None:
                if prev_month_orders > this_month_orders:
                    percentage =  ((prev_month_orders - this_month_orders)/prev_month_orders)*100
                    status = False
                elif prev_month_orders < this_month_orders:
                    percentage =  ((this_month_orders - prev_month_orders)/this_month_orders)*100
                    status = True
                else:
                    percentage = 0
                    status = False

                return GetTotalOrdersType(this_month_orders or 0, prev_month_orders or 0, round(percentage, 2) or 0, status)
            else:
                return GetTotalOrdersType(this_month_orders or 0, prev_month_orders or 0, percentage = 0, status = False)
        else:
            raise GraphQLError("Not an admin")

    def resolve_get_total_sales(root, info, start_date, end_date, token):
        auth = authenticate_user(token)
        if not auth["status"]:
           raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_admin:
            start_datetime = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_datetime = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
            previous_month_start = (start_datetime.replace(day=1) - timedelta(days=1)).replace(day=1)
            previous_month_end = start_datetime - timedelta(days=1)
            paid_order = Order.objects.filter(
                Q(paid=True) & Q(
                date_created__range=[start_datetime, end_datetime])).aggregate(total_sum=Sum('order_price_total')
                 )["total_sum"]
            prev_paid_order = Order.objects.filter(
                Q(paid=True) & Q(
                date_created__range=[previous_month_start, previous_month_end])).aggregate(prev_total_sum=Sum('order_price_total')
                 )["prev_total_sum"]
            print(prev_paid_order)
            if prev_paid_order and paid_order != None:
                if prev_paid_order > paid_order:
                    percentage =  ((prev_paid_order - paid_order)/prev_paid_order)*100
                    status = False
                elif prev_paid_order < paid_order:
                    percentage =  ((paid_order - prev_paid_order)/paid_order)*100
                    status = True
                else:
                    percentage = 0
                    status = False

                return GetTotalSalesType(paid_order or 0, prev_paid_order or 0, percentage, status)
            else:
                return GetTotalSalesType(paid_order or 0, prev_paid_order or 0, percentage = 0, status = False)
        else:
            raise GraphQLError("Not an admin")
            
    def resolve_get_average_sales(root, info, start_date, end_date, token):
        auth = authenticate_user(token)
        if not auth["status"]:
           raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_admin:
            start_datetime = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_datetime = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
            previous_month_start = (start_datetime.replace(day=1) - timedelta(days=1)).replace(day=1)
            previous_month_end = start_datetime - timedelta(days=1)
            paid_order = Order.objects.filter(
                Q(paid=True) & Q(
                date_created__range=[start_datetime, end_datetime])).aggregate(total_sum=Sum('order_price_total')
                 )["total_sum"]
            prev_paid_order = Order.objects.filter(
                Q(paid=True) & Q(
                date_created__range=[previous_month_start, previous_month_end])).aggregate(prev_total_sum=Sum('order_price_total')
                 )["prev_total_sum"]
            num_paid_order = Order.objects.filter(
                Q(paid=True) & Q(
                    date_created__range=[start_datetime, end_datetime])).count()
            prev_num_paid_order = Order.objects.filter(
                Q(paid=True) & Q(
                    date_created__range=[previous_month_start, previous_month_end])).count()
            if paid_order != None:
               average_sales = paid_order/num_paid_order
               if prev_paid_order != None:
                  prev_average_sales = prev_paid_order/prev_num_paid_order
                  if prev_average_sales > average_sales:
                        percentage =  ((prev_average_sales - average_sales)/prev_average_sales)*100
                        status = False
                  elif prev_average_sales < average_sales:
                        percentage =  ((average_sales - prev_average_sales)/average_sales)*100
                        status = True
                  else:
                        percentage = 0
                        status = False

               return GetAverageOrderValueType(round(average_sales, 3) or 0, round(prev_average_sales, 3) or 0, percentage, status)
            else:
                return GetAverageOrderValueType(round(average_sales, 3) or 0, prev_average_sales or 0, percentage = 0, status = False)
        else:
            raise GraphQLError("Not an admin")
        
    def resolve_get_total_active_customers(root, info, start_date, end_date, token):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user.is_admin:
            start_datetime = timezone.make_aware(
                datetime.strptime(start_date, '%Y-%m-%d'))
            end_datetime = timezone.make_aware(
                datetime.strptime(end_date, '%Y-%m-%d'))
            active_users = ExtendUser.objects.filter(Q(date_joined__range=[start_datetime, end_datetime]) & Q(is_active=True)).count()
            return GetTotalActiveCustomersType(active_users or 0)
        else:
            raise GraphQLError("Not an admin")
    