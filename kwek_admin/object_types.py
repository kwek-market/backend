import graphene
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

class GetTotalActiveCustomersType(graphene.ObjectType):
    active_customers = graphene.Int()