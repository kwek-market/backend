import re
import this
from typing_extensions import Required, Self
import graphene
import uuid
import random, math
from graphene_django import DjangoListField
from graphene.types.generic import GenericScalar
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
    fields
)

from notifications.object_types import MessageType
from kwek_admin.object_types import *
from wallet.models import Invoice, StoreDetail, Wallet, WalletTransaction
from wallet.object_types import *
from .model_object_type import UserType, SellerProfileType
from market.object_types import *
from users.models import SellerCustomer, ExtendUser, SellerProfile
from users.validate import authenticate_user, authenticate_admin
from django.db.models import Q
from bill.object_types import *
from operator import attrgetter
from .queries_build import build_products_query, build_users_query, get_price_range
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage



class Query(UserQuery, MeQuery, graphene.ObjectType):
    billing_address = graphene.Field(
        PickupType, address_id=graphene.String(required=True)
    )
    billing_addresses = DjangoListField(BillingType)
    categories = graphene.List(CategoryType, search=graphene.String(), visibility=graphene.String())
    get_user_by_id = graphene.Field(UserType, id=graphene.String(required=True), token=graphene.String(required=True))
    category = graphene.Field(CategoryType, id=graphene.String(required=True))
    contact_us = DjangoListField(ContactMessageType)
    coupons = graphene.Field(CouponPaginatedType, page=graphene.Int(), page_size=graphene.Int(),)
    cartitem = graphene.Field(CartItemType, id=graphene.String(required=True))
    deals_of_the_day = graphene.Field(
        ProductPaginatedType,
        page=graphene.Int(),
        page_size=graphene.Int(),
    )
    get_user_type = graphene.Field(
        GetUsersPaginatedType, token=graphene.String(required=True),
        seller = graphene.Boolean(),
        seller_is_rejected = graphene.Boolean(),
        seller_is_verified = graphene.Boolean(),
        customer = graphene.Boolean(),
        active = graphene.Boolean(),
        red_flagged = graphene.Boolean(),
        page=graphene.Int(),
        page_size=graphene.Int(),
        search=graphene.String()
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
    get_wallet_transactions = graphene.Field(
        WalletTransactionPaginatedType,
        token=graphene.String(required=True),
        search=graphene.String(),
        sort_by=graphene.String(),
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
    all_orders = graphene.Field(
        OrderPaginatedType, 
        token=graphene.String(required=True), 
        page=graphene.Int(),
        page_size=graphene.Int(),
        search=graphene.String(),
        product_id=graphene.String(),
        order_by=graphene.String()
        )
    order = graphene.Field(
        OrderType,
        token=graphene.String(required=True),
        id=graphene.String(required=True),
    )
    order_by_order_id = graphene.Field(
        OrderType,
        token=graphene.String(required=True),
        order_id=graphene.String(required=True),
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
    seller = graphene.Field(SellerProfileType, shop_url=graphene.String(required=True))
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
    get_customer_orders = graphene.Field(
        GetCustomerOrdersType,
        token = graphene.String(required=True),
        id = graphene.String(required=True),
    )
    get_customer_orders_paginated = graphene.Field(
        GetCustomerOrdersPaginatedType,
        token = graphene.String(required=True),
        id = graphene.String(required=True),
        page=graphene.Int(),
        page_size=graphene.Int(),

    )
    get_customer_average_order = graphene.Field(
        GetCustomerAverageOrderType,
        token = graphene.String(required=True),
        id = graphene.String(required=True)
    )
    get_customer_total_expense = graphene.Field(
        GetCustomerTotalSpentType,
        token = graphene.String(required=True),
        id = graphene.String(required=True)
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
    get_total_revenue = GenericScalar(
        token=graphene.String(required=True))
    
    get_recent_transactions = graphene.Field(GetRecentTransactionsPaginatedType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        start_date= graphene.String(required=True),
        end_date=graphene.String(required=True),
        token=graphene.String(required=True))
    get_refund_requests = graphene.Field(
        WalletRefundPaginatedType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        token=graphene.String(required=True)
    )
    get_flash_sales = graphene.Field(
        FlashSalesPaginatedType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        token=graphene.String(required=True)
    )
    get_refunds = graphene.Field(
        WalletRefundPaginatedType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        token=graphene.String(required=True)
    )
    get_seller_number_of_sales = graphene.Field(
        GetSellerSalesType,
        token = graphene.String(required=True),
        id = graphene.String(required=True)
    )
    get_seller_avg_sales = graphene.Field(
        GetAverageSellerType,
        token = graphene.String(required=True),
        id = graphene.String(required=True)
    )
    get_promoted_products_paginated = graphene.Field(
        ProductPaginatedType, 
        token=graphene.String(required=True),
        search=graphene.String(),
        page=graphene.Int(),
        page_size=graphene.Int(),
    )
    get_product_charge = graphene.List(
        ProductChargeType, 
    )
    get_state_delivery_fee = graphene.List(
        StateDeliveryType, 
    )
    state_delivery_fees = graphene.List(StateDeliveryFeeType)
    get_delivery_fee_for_a_state = graphene.Field(
        StateDeliveryType,
        state=graphene.String(required=True),
        city=graphene.String()
    )

    get_delivery_fee_by_id = graphene.Field(
        StateDeliveryType,
        id=graphene.String(required=True)
    )

    wishlists = graphene.List(WishlistItemType, token=graphene.String(required=True))
    
    def resolve_get_user_by_id(root, info, id, token):
        auth = authenticate_admin(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        return User.objects.get(id=id)
    
    def resolve_get_state_delivery_fee(root, info):
        state_fees = StateDeliveryFee.objects.all().order_by("-created_at")
        if len(state_fees) < 1:
            update_state_delivery_fees()
            state_fees = StateDeliveryFee.objects.all().order_by("-created_at")
        return state_fees
    
    def resolve_state_delivery_fees(self, info):
        # Get all state delivery fees from the database
        state_fees = StateDeliveryFee.objects.all()

        # Create a dictionary to group fees by state
        state_dict = {}
        for fee in state_fees:
            if fee.state not in state_dict:
                state_dict[fee.state] = []
            state_dict[fee.state].append({"city": fee.city, "fee": fee.fee, "id": fee.id})

        # Convert the dictionary to a list of StateDeliveryFeeType objects
        return [
            StateDeliveryFeeType(state=state, delivery_fees=[
                DeliveryFeeType(city=city_fee["city"], fee=city_fee["fee"], id=city_fees["id"])
                for city_fee in city_fees
            ]) for state, city_fees in state_dict.items()
        ]
    
    def resolve_get_delivery_fee_by_id(root, info,id):
        try:
            state_delivery_fee = StateDeliveryFee.objects.get(id=id)
            return state_delivery_fee
        except Exception as e:
            raise GraphQLError(e)
        
    def resolve_get_delivery_fee_for_a_state(root, info, state, city=""):  
        try:
            state_delivery_fee = get_delivery_fee_obj(state, city)
            return state_delivery_fee
        except Exception as e:
            raise GraphQLError(e)
       
    def resolve_get_product_charge(root, info):
        charge = ProductCharge.objects.all()
        if charge.exists():
            return charge
        raise GraphQLError("No product charge has been set!!")
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

    def resolve_categories(root, info, search=None, visibility=None):
        Category.objects.filter(visibility=Category.Visibility.SCHEDULED , publish_date__lte=datetime.now().date()).update(visibility=Category.Visibility.PUBLISHED)
        query = Q()

        if search:
            query = query & Q(name__icontains=search)

        if visibility:
            query = query & Q(visibility=visibility)

        if search or visibility:
            return Category.objects.filter(query, parent=None)
        return Category.objects.filter(parent=None)

    def resolve_category(root, info, id):
        return Category.objects.get(id=id)

    def resolve_contact_us(root, info):
        return ContactMessage.objects.all().order_by("-sent_at")

    def resolve_coupons(root, info, page=1, page_size=5):
        return get_paginator(Coupon.objects.all(), page_size, page, CouponPaginatedType)

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

    def resolve_seller(root, info, shop_url):
        try:
            seller = SellerProfile.objects.get(shop_url=shop_url)
            return seller
        except Exception as e:
            raise GraphQLError("seller's shop not found")


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
                        cart_items = CartItem.objects.filter(cart=cart, ordered=False).check_and_update_items()
                    else:
                        cart_items = []
                except Exception as e:
                    print("error", e)
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
                prods = Product.objects.filter(user=user).order_by("-date_created")
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
                            sort_key, "-date_created"
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
                        ).order_by(v1, v2, "-date_created")
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
                                    .order_by(sort_key, "-date_created")
                                )
                            else:
                                prods = (
                                    prods.annotate(
                                        rate=Sum("product_rating__rating")
                                        / Count("product_rating__rating")
                                    )
                                    .filter(rate__gte=abs(rating))
                                    .order_by(sort_key, "-date_created")
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
        prods = build_products_query(search, sort_by, keyword, price_range, rating, sizes)
        return get_paginator(prods, page_size, page, ProductPaginatedType)

    def resolve_review(root, info, review_id):
        review = Rating.objects.get(id=review_id)

    def resolve_reviews(root, info, page, page_size, product_id=None, sort_by=None):
        reviews = []
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
            promoted_products = Product.objects.filter(user=user, promoted=True).order_by("-date_created")
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

    def resolve_all_orders(root, info, token, page, page_size=50, search=None,product_id=None, order_by='-date_created'):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        orders = Order.objects.all().order_by(order_by)
        if search:
            search_filter = (
            Q(order_id__icontains=search)
            | Q(user__full_name__icontains=search)
            )
            orders = orders.filter(search_filter)

        if product_id:
            orders = orders.filter(cart_items__product__id=product_id).distinct()
        return get_paginator(orders, page_size, page, OrderPaginatedType)

    def resolve_order(root, info, token, id):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        user_order = Order.objects.get( id=id)
        return user_order

    def resolve_order_by_order_id(root, info, token, order_id):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        user_order = Order.objects.get( order_id=order_id)
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

    # def resolve_get_seller_orders(
    #     root, info, token, page=1, page_size=50, this_month=False
    # ):
    #     auth = authenticate_user(token)
    #     if not auth["status"]:
    #         raise GraphQLError(auth["message"])
    #     user, seller_orders, this_month_filter = auth["user"], [], Q()
    #     if this_month:
    #         this_month_filter = Q(date_created__month=datetime.now().month) & Q(
    #             date_created__year=datetime.now().year
    #         )
    #     charge = SellerProfile.objects.get(user=user).kwek_charges
    #     orders = Order.objects.filter(this_month_filter, cart_items__product__user=user).order_by("-date_created")

    #     orders_values = orders.values(
    #         "order_id",
    #         "date_created",
    #         "user__id",
    #         "paid",
    #         "cart_items__price",
    #         "progress__progress",
    #     )
    #     print(orders_values)
    #     for i in orders_values:
    #         seller_orders.append(
    #             GetSellerOrdersType(
    #                 order=Order.objects.get(order_id=i["order_id"]),
    #                 created=str(i["date_created"]),
    #                 customer=ExtendUser.objects.get(id=i["user__id"]),
    #                 total=int(i["cart_items__price"]),
    #                 profit=int(i["cart_items__price"])
    #                 - (int(i["cart_items__price"]) * charge),
    #                 paid=i["paid"],
    #                 status=i["cart_items__price"],
    #             )
    #         )
    #     return get_paginator(
    #         seller_orders, page_size, page, GetSellerOrdersPaginatedType
    #     )

    def resolve_get_seller_orders(root, info, token, page=1, page_size=50, this_month=False):
        auth = authenticate_user(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])

        user = auth["user"]
        this_month_filter = Q()
        if this_month:
            now = datetime.now()
            this_month_filter = Q(date_created__month=now.month, date_created__year=now.year)
        
        # Calculate the profit using annotations
        charge = SellerProfile.objects.get(user=user).kwek_charges
        profit_expression = ExpressionWrapper(
            F('cart_items__price') - (F('cart_items__price') * charge),
            output_field=FloatField()
        )

         # Prefetch only the relevant CartItems
        cart_items_prefetch = Prefetch(
            'cart_items',
            queryset=CartItem.objects.filter(product__user=user)
        )

        # Apply filtering, annotation, and ordering before pagination
        orders = Order.objects.filter(this_month_filter, cart_items__product__user=user) \
            .annotate(
                total_price=Sum('cart_items__price'),
                profit=profit_expression,
                customer_id=F('user__id'),
                status=F('progress__progress')
            ) \
            .prefetch_related(cart_items_prefetch) \
            .order_by('-date_created')
        
        # Apply pagination at the query level
        paginator = Paginator(orders, page_size)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        seller_orders = [
        GetSellerOrdersType(
            order=order,  # Directly use the order object
            created=str(order.date_created),
            customer=ExtendUser.objects.get(id=order.customer_id),
            total=order.total_price,
            profit=order.profit,
            paid=order.paid,
            status=order.status,
        )
        for order in page_obj.object_list
        ]

    #     (
    #     page=page_obj.number,
    #     pages=p.num_pages,
    #     has_next=page_obj.has_next(),
    #     has_prev=page_obj.has_previous(),
    #     objects=page_obj.object_list,
    #     **kwargs
    # )

        return get_paginator(seller_orders, page_size, page, GetSellerOrdersPaginatedType)

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
        auth = authenticate_admin(token)
        if not auth["status"]:
           raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
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
 

    def resolve_get_total_sales(root, info, start_date, end_date, token):
        auth = authenticate_admin(token)
        if not auth["status"]:
           raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            start_datetime = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_datetime = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
            previous_month_start = (start_datetime.replace(day=1) - timedelta(days=1)).replace(day=1)
            previous_month_end = start_datetime - timedelta(days=1)
            paid_order = Order.objects.filter(
                paid=True,
                date_created__range=[start_datetime, end_datetime]).aggregate(total_sum=Sum('order_price_total')
                 )["total_sum"]
            prev_paid_order = Order.objects.filter(
                paid=True,
                date_created__range=[previous_month_start, previous_month_end]).aggregate(prev_total_sum=Sum('order_price_total')
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

            
    def resolve_get_average_sales(root, info, start_date, end_date, token):
        auth = authenticate_admin(token)
        if not auth["status"]:
           raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            start_datetime = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_datetime = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
            previous_month_start = (start_datetime.replace(day=1) - timedelta(days=1)).replace(day=1)
            previous_month_end = start_datetime - timedelta(days=1)
            paid_order = Order.objects.filter(
                paid=True,
                date_created__range=[start_datetime, end_datetime]).aggregate(total_sum=Sum('order_price_total')
                 )["total_sum"]
            prev_paid_order = Order.objects.filter(
                paid=True,
                date_created__range=[previous_month_start, previous_month_end]).aggregate(prev_total_sum=Sum('order_price_total')
                 )["prev_total_sum"]
            num_paid_order = Order.objects.filter(
                paid=True,
                    date_created__range=[start_datetime, end_datetime]).count()
            prev_num_paid_order = Order.objects.filter(
                paid=True,
                    date_created__range=[previous_month_start, previous_month_end]).count()
            average_sales = 0
            prev_average_sales = 0
            if paid_order != None:
               average_sales = paid_order/num_paid_order
               prev_average_sales = 0
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
                    return GetAverageOrderValueType(round(average_sales, 3) or 0, round(prev_average_sales, 3) or 0, percentage = 0, status = False)
            else:
                return GetAverageOrderValueType(round(average_sales, 3) or 0, round(prev_average_sales, 3) or 0, percentage = 0, status = False)
        
    def resolve_get_total_active_customers(root, info, token, start_date, end_date):
        auth = authenticate_admin(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            start_datetime = timezone.make_aware(
                datetime.strptime(start_date, '%Y-%m-%d'))
            end_datetime = timezone.make_aware(
                datetime.strptime(end_date, '%Y-%m-%d'))
            active_users = Order.objects.filter(date_created__range=[start_datetime, end_datetime], paid=True).order_by("user_id").distinct("user_id").count()
            return GetTotalActiveCustomersType(active_users or 0)
    
    def resolve_get_total_revenue(root, info, token):
        auth = authenticate_admin(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            data = {}
            for i in range(1, 13):
                revenue = Order.objects.filter(paid=True, date_created__month=i, date_created__year=datetime.now().year).aggregate(monthly_revenue = Sum('order_price_total'))
                if revenue["monthly_revenue"]:
                  data[i] = revenue["monthly_revenue"]
                else:
                  data[i] = 0
            return data

    def resolve_get_recent_transactions(root, info, token,start_date, end_date, page=1, page_size=50):
        auth = authenticate_admin(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            start_datetime = timezone.make_aware(
                datetime.strptime(start_date, '%Y-%m-%d'))
            end_datetime = timezone.make_aware(
                datetime.strptime(end_date, '%Y-%m-%d'))
            recent_transactions = Order.objects.filter(date_created__range=[start_datetime, end_datetime], paid=True).order_by("-date_created")
            return get_paginator(
                recent_transactions, page_size, page, GetRecentTransactionsPaginatedType
            )
        
    def resolve_get_user_type(
            root, info, 
            token, 
            seller=None, 
            seller_is_rejected=None,
            seller_is_verified=None,
            customer=None, 
            active=True,
            red_flagged=False, 
            page=1, 
            page_size=50,
            search=None
            ):
        auth = authenticate_admin(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
           users = build_users_query(seller, seller_is_rejected,seller_is_verified, customer, active, red_flagged, search)
           return get_paginator(users, page_size, page, GetUsersPaginatedType)
        else:
            raise GraphQLError("invalid authentication")
    
    def resolve_get_customer_orders(root, info, token, id):
        auth = authenticate_admin(token)
        if not auth["status"]:
          raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:

            customer_orders = Order.objects.filter(user_id=id).count()
            return GetCustomerOrdersType(customer_orders)
            
    def resolve_get_customer_orders_paginated(root, info, token, id, page=1, page_size=50):
        auth = authenticate_admin(token)
        if not auth["status"]:
          raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
                customer_orders = Order.objects.filter(user_id=id).order_by("-date_created")
                return get_paginator(customer_orders, page_size, page, GetCustomerOrdersPaginatedType)
            

    def resolve_get_refund_requests(root, info, token, page=1, page_size=50):
        auth = authenticate_admin(token)
        if not auth["status"]:
          raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            refund_requests = WalletRefund.objects.filter(status=False).order_by("-date_created")
            return get_paginator( refund_requests, page_size, page, WalletRefundPaginatedType)
            
    
    def resolve_get_refunds(root, info, token, page=1, page_size=50):
        auth = authenticate_admin(token)
        if not auth["status"]:
          raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            refund_requests = WalletRefund.objects.filter(status=True).order_by("-date_created")
            return get_paginator( refund_requests, page_size, page, WalletRefundPaginatedType)
           
    
    def resolve_get_flash_sales(root, info, token, page=1, page_size=50):
        auth = authenticate_admin(token)
        if not auth["status"]:
          raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            FlashSales.objects.filter(
                start_date__lte=timezone.now() - (timedelta(days=1) * F('number_of_days')),
                status=True
            ).update(status=False)
            flash_sales = FlashSales.objects.filter(status=True).order_by("-start_date")
            return get_paginator( flash_sales, page_size, page, FlashSalesPaginatedType)
            
    
    def resolve_get_customer_average_order(root, info, token, id):
        auth = authenticate_admin(token)
        if not auth["status"]:
          raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            customer_order_no = Order.objects.filter(user_id=id, paid=True).count()
            customer_orders = Order.objects.filter(user_id=id, paid=True).aggregate(total_sum=Sum('order_price_total'))["total_sum"]
            average_order_value = (customer_orders if customer_orders else 0 /customer_order_no) if customer_order_no else 0
            print("average_order_value", average_order_value)
            return GetCustomerAverageOrderType(round(average_order_value, 3) or 0)
            
    
    def resolve_get_customer_total_expense(root, info, token, id):
        auth = authenticate_admin(token)
        if not auth["status"]:
          raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            customer_total_expense = Order.objects.filter(user_id=id, paid=True).aggregate(total_sum=Sum('order_price_total'))["total_sum"]
            return GetCustomerTotalSpentType(round(customer_total_expense if customer_total_expense else 0, 3) or 0)
    
    def resolve_get_seller_number_of_sales(root, info, token, id):
        auth = authenticate_admin(token)
        if not auth["status"]:
          raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            seller_sales = Sales.objects.filter(
                product__user=id,
            ).count()
            return seller_sales or 0
    
    def resolve_seller_avg_sales(root, info, token, id):
        auth = authenticate_admin(token)
        if not auth["status"]:
          raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            seller_sales = Sales.objects.filter(
                product__user=id,
            ).count()
            seller_total_sales = Sales.objects.filter(
                product__user=id
            ).aggregate(total_sales=Sum("amount"))["total_sales"]
            avg_sales = seller_total_sales/seller_sales
            return round(avg_sales, 3) or 0
        
    def resolve_get_promoted_products_paginated(root, info, token, page=1, page_size=50, search=None, ):
        auth = authenticate_admin(token)
        if not auth["status"]:
          raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            promoted_products = Product.objects.filter(promoted=True).order_by("-date_created")
            search_filter = Q()
            search_status = False
            if search:
                search_status = True
                search_filter=(
                    Q(user__full_name__icontains=search)
                    |Q(product_title__icontains=search)
                )
            if search_status:
                promoted_products = promoted_products.filter(search_filter).order_by("-date_created")
            return get_paginator(promoted_products,page_size,page, ProductPaginatedType)
        
    def resolve_get_wallet_transactions(root, info, token, page=1, page_size=50, search=None, sort_by=None):
        auth = authenticate_admin(token)
        if not auth["status"]:
            raise GraphQLError(auth["message"])
        user = auth["user"]
        if user:
            transactions = WalletTransaction.objects.all().order_by("-date")
            search_filter = Q()
            search_status = False
            if search:
                search_status = True
                search_filter=(
                    Q(id__icontains=search)
                )   
            if search_status:
                transactions=transactions.filter(search_filter)
            if sort_by:
                if sort_by in [
                    "deposit",
                    "withdrawal",
                ]:
                    transactions=transactions.filter(transaction_type__icontains = sort_by)
                else:
                    transactions=transactions
            return get_paginator(
                transactions, page_size, page, WalletTransactionPaginatedType
            )
            
