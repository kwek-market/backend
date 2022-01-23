import graphene
import jwt

from django.conf import settings
from market.pusher import push_to_client

from notifications.models import Message, Notification

from .models import (
    Invoice,
    StoreDetail,
    Wallet,
    PurchasedItem,
    WalletTransaction
)

from .object_types import (
    InvoiceType,
    WalletType
)

from users.models import ExtendUser, SellerProfile
from users.validate import authenticate_user









class CreateInvoice(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    invoice = graphene.Field(InvoiceType)

    class Arguments:
        token = graphene.String(required=True)
        customer_name = graphene.String(required=True)
        customer_email = graphene.String(required=True)
        customer_address = graphene.String(required=True)
        purchased_item = graphene.List(graphene.String, required=True)
        delivery_fee = graphene.Int(required=True)
        subtotal = graphene.Int(required=True)
        total = graphene.Int(required=True)
        note = graphene.String()
    
    @staticmethod
    def mutate(
        self,
        info,
        token,
        customer_name,
        customer_email,
        customer_address,
        purchased_item,
        delivery_fee,
        subtotal,
        total,
        note=None
    ):
        auth = authenticate_user(token)
        if not auth["status"]:
            return CreateInvoice(status=auth["status"],message=auth["message"])
        user = auth["user"]

        if not StoreDetail.objects.filter(user=user).exists():
            seller = SellerProfile.objects.get(user=user)
            store = StoreDetail.objects.create(
                user=user,
                store_name=seller.shop_name,
                email=user.email,
                address=seller.shop_address
            )
        else:
            store = StoreDetail.objects.get(user=user)
        
        if user:
            try:
                invoice = Invoice.objects.create(
                    store=store,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_address=customer_address,
                    delivery_fee=delivery_fee,
                    subtotal=subtotal,
                    total=total,
                    note=note
                )

                for items in purchased_item:
                    item = eval(items)
                    PurchasedItem.objects.create(
                        invoice=invoice,
                        item=item["item"],
                        description=item["description"],
                        quantity=item["quantity"],
                        unit_cost=item["unit_cost"],
                        total=item["total"],
                    )
                
                return CreateInvoice(
                    invoice=invoice,
                    status=True,
                    message="Invoice created"
                )
            except Exception as e:
                return CreateInvoice(status=False,message=e)
        else:
            return CreateInvoice(status=False,message="Invalid User")

class FundWallet(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    wallet = graphene.Field(WalletType)

    class Arguments:
        token = graphene.String(required=True)
        remark = graphene.String(required=True)
        amount = graphene.Int(required=True)
    
    @staticmethod
    def mutate(self, info, token, remark, amount):
        auth = authenticate_user(token)
        if not auth["status"]:
            return FundWallet(status=auth["status"],message=auth["message"])
        user = auth["user"]
        if Wallet.objects.filter(owner=user).exists():
            try:
                seller_wallet = Wallet.objects.get(owner=user)
                wallet = WalletTransaction.objects.create(
                    wallet=seller_wallet,
                    amount=amount,
                    remark=remark,
                    transaction_type="Funding"
                )
                balance = seller_wallet.balance
                new_balance = balance + amount
                Wallet.objects.filter(owner=user).update(balance=new_balance)
                if Notification.objects.filter(user=user).exists():
                    notification = Notification.objects.get(
                        user=user
                    )
                else:
                    notification = Notification.objects.create(
                        user=user
                    )
                notification_message = Message.objects.create(
                    notification=notification,
                    message=f"{amount} was added to your wallet successfully",
                    subject="Fund wallet"
                )
                notification_info = {"notification":str(notification_message.notification.id),
                "message":notification_message.message, 
                "subject":notification_message.subject}
                push_to_client(user.id, notification_info)

                return FundWallet(
                    status=True,
                    message="Wallet funded",
                    wallet=wallet
                )
            except Exception as e:
                return FundWallet(status=False,message=e)
        else:
            return FundWallet(status=False,message="User has no wallet")

class WithdrawFromWallet(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    wallet = graphene.Field(WalletType)

    class Arguments:
        token = graphene.String(required=True)
        amount = graphene.Int(required=True)
    
    @staticmethod
    def mutate(self, info, token, remark, amount):
        auth = authenticate_user(token)
        if not auth["status"]:
            return WithdrawFromWallet(status=auth["status"],message=auth["message"])
        user = auth["user"]
        if user:
            if Wallet.objects.filter(owner=user).exists():
                try:
                    seller_wallet = Wallet.objects.get(owner=user)
                    if seller_wallet.balance < amount:
                        return {
                            "status": False,
                            "message": "Insufficient balance"
                        }
                    else:
                        wallet = WalletTransaction.objects.create(
                            wallet=seller_wallet,
                            amount=amount,
                            remark="Withdrawal",
                            transaction_type="Withdrawal"
                        )
                        balance = seller_wallet.balance
                        new_balance = balance - amount
                        Wallet.objects.filter(owner=user).update(balance=new_balance)
                        if Notification.objects.filter(user=user).exists():
                            notification = Notification.objects.get(
                                user=user
                            )
                        else:
                            notification = Notification.objects.create(
                                user=user
                            )
                        notification_message = Message.objects.create(
                            notification=notification,
                            message=f"{amount} was withdrawn from your wallet successfully",
                            subject="Withdraw"
                        )
                        notification_info = {"notification":str(notification_message.notification.id),
                        "message":notification_message.message, 
                        "subject":notification_message.subject}
                        push_to_client(user.id, notification_info)

                        return FundWallet(
                            status=True,
                            message="Withdrawal successful",
                            wallet=wallet
                        )
                except Exception as e:
                    return WithdrawFromWallet(status=False,message=e)
            else:
                return WithdrawFromWallet(status=False,message="User has no wallet")
        else:
            return WithdrawFromWallet(status=False,message="Invalid user")


class WalletTransactionSuccess(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String
    wallet = graphene.Field(WalletType)

    class Arguments:
        token = graphene.String(required=True)
        wallet_transaction_id = graphene.String(required=True)
    
    @staticmethod
    def mutate(self, info, token, wallet_transaction_id):
        auth = authenticate_user(token)
        if not auth["status"]:
            return WithdrawFromWallet(status=auth["status"],message=auth["message"])
        user = auth["user"]
        try:
            seller_wallet = WalletTransaction.objects.filter(owner=user, transaction__id=wallet_transaction_id)
            if seller_wallet.exists():
                seller_wallet.update(status=True)

                return WalletTransactionSuccess(
                    status=True,
                    message="Status updated",
                    wallet=seller_wallet
                )
            else:
                return WalletTransactionSuccess(
                    status=False,
                    message="Wallet transaction does not exist"
                )
        except Exception as e:
            return WalletTransactionSuccess(
                    status=False,
                    message=e
                )

