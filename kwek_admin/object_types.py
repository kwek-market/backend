import graphene
from market.object_types import *
from users.model_object_type import *
from graphene_django import DjangoObjectType

class GetTotalOrdersType(graphene.ObjectType):
    total_orders = graphene.Int()
    prev_orders = graphene.Int()
    percentage = graphene.Int()
    status =  graphene.Boolean()

class GetTotalSalesType(graphene.ObjectType):
    total_sales = graphene.Float()
    prev_sales = graphene.Int()
    percentage = graphene.Int()
    status =  graphene.Boolean()

class GetAverageOrderValueType(graphene.ObjectType):
    average_order_value = graphene.Float()
    prev_average_order_value = graphene.Int()
    percentage = graphene.Int()
    status =  graphene.Boolean()

class GetRecentTransactionsPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()                                     
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(OrderType)

class GetUsersPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()                                     
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(UserType)

class GetTotalActiveCustomersType(graphene.ObjectType):
    active_customers = graphene.Int()

class GetCustomerOrdersType(graphene.ObjectType):
    total_orders = graphene.Int()

class GetCustomerOrdersPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()                                     
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(OrderType)

class GetCustomerAverageOrderType(graphene.ObjectType):
    average_order_value = graphene.Float()


class GetCustomerTotalSpentType(graphene.ObjectType):
    total_spent = graphene.Float()

class GetSellerSalesType(graphene.ObjectType):
    total_sales = graphene.Int()


class GetAverageSellerType(graphene.ObjectType):
    Average_sales = graphene.Float()