from graphene_django import DjangoObjectType
import graphene
from .models import (
    StoreDetail,
    PurchasedItem,
    Invoice,
    Wallet,
    WalletTransaction,
    WalletRefund
)





class StoreDetailType(DjangoObjectType):
    class Meta:
        model = StoreDetail

class PurchasedItemType(DjangoObjectType):
    class Meta:
        model = PurchasedItem

class InvoiceType(DjangoObjectType):
    class Meta:
        model = Invoice

class WalletType(DjangoObjectType):
    class Meta:
        model = Wallet

class WalletRefundType(DjangoObjectType):
    class Meta:
        model = WalletRefund

class WalletTransactionType(DjangoObjectType):
    class Meta:
        model = WalletTransaction

class InvoicePaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(InvoiceType)

class WalletTransactionPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(WalletTransactionType)

class WalletRefundPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(WalletRefundType)