from graphene_django import DjangoObjectType

from .models import (
    StoreDetail,
    PurchasedItem,
    Invoice,
    Wallet,
    WalletTransaction
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

class WalletTransactionType(DjangoObjectType):
    class Meta:
        model = WalletTransaction
