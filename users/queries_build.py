from market.object_types import *
from django.db.models import Q
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
    Sum
)
from graphql import GraphQLError
from users.models import SellerCustomer, ExtendUser, SellerProfile

def get_price_range(range):
    try:
        return range[0], range[1]
    except:
        raise GraphQLError("wrong price range data")
    
def build_users_query(
        seller=None, 
            seller_is_rejected=None,
            customer=None, 
            active=True,
            red_flagged=False, 
            search=None,
):
    users = {}
    search_filter, user_type_filter = Q(), Q()
    has_search, has_user_filter = False, False
    if search:
        has_search = True
        search_filter = (
            Q(email__icontains=search)
            | Q(full_name__icontains=search)
            | Q(seller_profile__firstname__icontains=search)
            | Q(seller_profile__lastname__icontains=search)
            | Q(seller_profile__state__icontains=search)
            | Q(seller_profile__city__icontains=search)
        )

    if seller:
        has_user_filter = True
        user_type_filter = Q(is_seller=seller, is_active=active, is_flagged=red_flagged) 
        if seller_is_rejected:
            user_type_filter = user_type_filter & Q(seller_is_rejected=seller_is_rejected)

    if customer:
        has_user_filter = True
        user_type_filter = Q(is_seller=False, is_active=active, is_flagged=red_flagged)

    if has_user_filter and has_search:
        users = ExtendUser.filter(search_filter, user_type_filter)
    elif not has_user_filter and has_search:
        users = ExtendUser.filter(search_filter)
    elif has_user_filter and not has_search:
        users = ExtendUser.filter(user_type_filter)
    else:
        users = ExtendUser.objects.all().order_by('-date_joined')
    
    return users



def build_products_query(
        search=None,
        sort_by=None,
        keyword=None,
        price_range=None,
        rating=None,
        sizes=None):
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

        return prods