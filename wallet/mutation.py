import graphene

from django.contrib.auth import authenticate
from bill.models import *
from market.pusher import SendEmailNotification, push_to_client
import json, ast

from notifications.models import Message, Notification

from .models import (
    Invoice,
    StoreDetail,
    Wallet,
    PurchasedItem,
    WalletTransaction,
    WalletRefund
    
)

from .object_types import (
    InvoiceType,
    WalletType,
    WalletRefundType
    
)

from users.models import ExtendUser, SellerProfile
from users.validate import authenticate_user, authenticate_admin



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

                for item_string in purchased_item:
                    try:
                        json_acceptable_string = item_string.replace("'", "\"")
                        item = json.loads(json_acceptable_string)
                        PurchasedItem.objects.create(
                            invoice=invoice,
                            item=item["item"],
                            description=item["description"],
                            quantity=item["quantity"],
                            unit_cost=item["unit_cost"],
                            total=item["total"],
                        )
                    except Exception as e:
                        return CreateInvoice(status=False,message=e)
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
        payment_ref = graphene.String(required=True)
    
    @staticmethod
    def mutate(self, info, token, remark, payment_ref):
        auth = authenticate_user(token)
        if not auth["status"]:
            return FundWallet(status=auth["status"],message=auth["message"])
        user = auth["user"]
        amount = 0
        p_status = False
        if Wallet.objects.filter(owner=user).exists():
            if Payment.objects.filter(ref=payment_ref).exists():
                payment = Payment.objects.get(ref=payment_ref)
                if payment.verified:
                    if payment.used:
                        return FundWallet(
                            status = False,
                            message = "Payment is invalid"
                        )
                    else:
                        amount = payment.amount
                        p_status=True
                else:
                    return FundWallet(
                        status = False,
                        message = "Payment has not been verified"
                    )
                
                try:
                    seller_wallet = Wallet.objects.get(owner=user)
                    wallet = WalletTransaction.objects.create(
                        wallet=seller_wallet,
                        amount=amount,
                        remark=remark,
                        status=p_status,
                        transaction_type="Funding"
                    )
                    balance = seller_wallet.balance
                    new_balance = balance + amount
                    Wallet.objects.filter(owner=user).update(balance=new_balance)

                    payment.used = True
                    payment.save()
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
                    email_send = SendEmailNotification(user.email)
                    email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)

                    return FundWallet(
                        status=True,
                        message="Wallet funded",
                        wallet=wallet
                    )
                except Exception as e:
                    return FundWallet(status=False,message=e)
            else:
                return FundWallet(
                    status = False,
                    message = "Invalid Payment reference"
                )
        else:
            return FundWallet(status=False,message="User has no wallet")

class WithdrawFromWallet(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    wallet = graphene.Field(WalletType)

    class Arguments:
        token = graphene.String(required=True)
        password = graphene.String(required=True)
        amount = graphene.Int(required=True)
    
    @staticmethod
    def mutate(self, info, token, password, amount):
        auth = authenticate_user(token)
        if not auth["status"]:
            return WithdrawFromWallet(status=auth["status"],message=auth["message"])
        user = auth["user"]
        a_user = authenticate(username=user.email, password=password)
        if user == a_user:
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
                        email_send = SendEmailNotification(user.email)
                        email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)

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
            return WalletTransactionSuccess(status=auth["status"],message=auth["message"])
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

class RefundRequest(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    refund = graphene.Field(WalletRefundType)

    class Arguments:
        token = graphene.String(required=True)
        order_id = graphene.String(required=True)
        cart_item_id = graphene.String(required=True)
        account_number = graphene.String(required=True)
        bank_name = graphene.String(required=True)
        number_of_product = graphene.String()
        
    @staticmethod
    def mutate(self, info, token, cart_item_id, order_id, account_number, bank_name, number_of_product=1):
        auth = authenticate_user(token)
        if not auth["status"]:
            return RefundRequest(status=auth["status"],message=auth["message"])
        try:
            if Order.objects.filter(id=order_id).exists() and CartItem.objects.filter(id=cart_item_id).exists():
               order = Order.objects.get(id=order_id)
               number_of_cartitems= order.cart_items.count()
               order_product = order.cart_items.filter(id=cart_item_id)
               if  order_product.exists():
                   product = order_product.get(id=cart_item_id)
                   if WalletRefund.objects.filter(order=order).exists():
                        order_refund_request = WalletRefund.objects.filter(order=order).count()
                        product_refund_request = WalletRefund.objects.filter(order=order, product=product).count()
                        if (order_refund_request > number_of_cartitems) or (product_refund_request > order_product.count()):
                                return RefundRequest(status= False, message="Already refunded for that product")
               else:
                   return RefundRequest(status= False, message="Cart item does not exist in order")
                  
               refund_request = WalletRefund.objects.create(
                   order=order,
                   account_number=account_number,
                   product=product,
                   bank_name=bank_name,
                   number_of_product=number_of_product
               )

               return RefundRequest(status= True, message="Refund in progress", refund=refund_request)   
            else:
               return RefundRequest(status= False, message="Could not find order")      
        except Exception as e:
            return RefundRequest(status= False, message=e)   

class ForceRefund(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments():
        token = graphene.String(required=True)
        refund_id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, token, refund_id):
        auth = authenticate_user(token)
        if not auth["status"]:
            return ForceRefund(status=auth["status"],message=auth["message"])
        try:

            if WalletRefund.objects.filter(id=refund_id).exists():
                refund_item = WalletRefund.objects.get(id=refund_id)
                if not refund_item.status:
                    refunded_item = CartItem.objects.get(id=refund_item.product.id)
                    refunded_item_seller = Product.objects.get(id=refunded_item.product.id).user
                    item_price = round(refunded_item.price * refund_item.number_of_product, 2)
                    seller_wallet = Wallet.objects.get(owner=refunded_item_seller.id)
                    refund_amount = seller_wallet.balance - item_price
                    seller_wallet.balance = refund_amount
                    seller_wallet.save()
                    refund_item.status=True
                    refund_item.save()
                    return ForceRefund(status=True, message="Amount successfully deducted from sellers wallet")
                return ForceRefund(status=False, message="Already refunded")
            return ForceRefund(status=False, message="Refund does not exist")
        except Exception as e:
            
            return ForceRefund(status=False, message=e)
            
            
                





