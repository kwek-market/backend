import graphene
from market.models import Cart, CartItem, Product, ProductOption
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
            return FundWallet(status=auth["status"], message=auth["message"])

        user = auth["user"]

        try:
            # Verify wallet exists
            if not Wallet.objects.filter(owner=user).exists():
                return FundWallet(status=False, message="User has no wallet")

            # Verify payment
            if not Payment.objects.filter(ref=payment_ref).exists():
                return FundWallet(status=False, message="Invalid Payment reference")

            payment = Payment.objects.get(ref=payment_ref)
            if not payment.verified:
                return FundWallet(status=False, message="Payment has not been verified")

            if payment.used:
                return FundWallet(status=False, message="Payment is invalid")

            amount = payment.amount
            seller_wallet = Wallet.objects.get(owner=user)

            # Create transaction first
            wallet_transaction = WalletTransaction.objects.create(
                wallet=seller_wallet,
                amount=amount,
                remark=remark,
                status=True,  # Set to True since we verified payment
                transaction_type="Funding",
            )

            # Update wallet balance
            seller_wallet.balance += amount
            seller_wallet.save()

            # Mark payment as used
            payment.used = True
            payment.save()

            # Handle notifications
            notification = Notification.objects.get_or_create(user=user)[0]
            notification_message = Message.objects.create(
                notification=notification,
                message=f"{amount} was added to your wallet successfully",
                subject="Fund wallet",
            )

            notification_info = {
                "notification": str(notification_message.notification.id),
                "message": notification_message.message,
                "subject": notification_message.subject,
            }

            push_to_client(user.id, notification_info)

            # Send email notification
            email_send = SendEmailNotification(user.email)
            email_send.send_only_one_paragraph(
                notification_message.subject, notification_message.message
            )

            return FundWallet(
                status=True, message="Wallet funded", wallet=seller_wallet
            )

        except Exception as e:
            return FundWallet(status=False, message=str(e))


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
        try:
            auth = authenticate_user(token)
            if not auth["status"]:
                return WithdrawFromWallet(status=False, message=auth["message"])

            user = auth["user"]
            a_user = authenticate(username=user.email, password=password)

            if not a_user:
                return WithdrawFromWallet(status=False, message="Invalid user")

            try:
                seller_wallet = Wallet.objects.get(owner=user)
            except Wallet.DoesNotExist:
                return WithdrawFromWallet(status=False, message="User has no wallet")

            if seller_wallet.balance < amount:
                return WithdrawFromWallet(status=False, message="Insufficient balance")

            # Create transaction first
            wallet_transaction = WalletTransaction.objects.create(
                wallet=seller_wallet,
                amount=amount,
                remark="Withdrawal",
                status=True,
                transaction_type="Withdrawal",
            )

            # Update balance
            seller_wallet.balance = seller_wallet.balance - amount
            seller_wallet.save()

            # Handle notifications
            notification, created = Notification.objects.get_or_create(user=user)

            notification_message = Message.objects.create(
                notification=notification,
                message=f"{amount} was withdrawn from your wallet successfully",
                subject="Withdraw",
            )

            notification_info = {
                "notification": str(notification_message.notification.id),
                "message": notification_message.message,
                "subject": notification_message.subject,
            }
            push_to_client(user.id, notification_info)

            email_send = SendEmailNotification(user.email)
            email_send.send_only_one_paragraph(
                notification_message.subject, notification_message.message
            )

            return WithdrawFromWallet(
                status=True, message="Withdrawal successful", wallet=seller_wallet
            )

        except Exception as e:
            return WithdrawFromWallet(status=False, message=str(e))


class WalletTransactionSuccess(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    wallet = graphene.Field(WalletType)

    class Arguments:
        token = graphene.String(required=True)
        wallet_transaction_id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, token, wallet_transaction_id):
        try:
            auth = authenticate_user(token)
            if not auth["status"]:
                return WalletTransactionSuccess(status=False, message=auth["message"])

            user = auth["user"]

            try:
                transaction = WalletTransaction.objects.get(id=wallet_transaction_id)
            except WalletTransaction.DoesNotExist:
                return WalletTransactionSuccess(
                    status=False, message="Invalid transaction ID"
                )

            if transaction.wallet.owner != user:
                return WalletTransactionSuccess(
                    status=False, message="Unauthorized access to this transaction"
                )

            if transaction.status:
                return WalletTransactionSuccess(
                    status=False, message="Transaction already processed"
                )

            # Update transaction status
            transaction.status = True
            transaction.save()

            # Update wallet balance
            wallet = transaction.wallet
            if transaction.transaction_type == "Funding":
                wallet.balance += transaction.amount
            elif transaction.transaction_type == "Withdrawal":
                if wallet.balance < transaction.amount:
                    return WalletTransactionSuccess(
                        status=False, message="Insufficient balance"
                    )
                wallet.balance -= transaction.amount

            wallet.save()

            return WalletTransactionSuccess(
                status=True, message="Transaction processed successfully", wallet=wallet
            )

        except Exception as e:
            return WalletTransactionSuccess(status=False, message=str(e))


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
                order = Order.objects.filter(id=order_id).first()
                cart_item = CartItem.objects.filter(id=cart_item_id).first()
                
                if not order:
                    return RefundRequest(status= False, message="Could not find order")      
                if not cart_item:
                    return RefundRequest(status= False, message="Cart item does not exist in order")
                number_of_cartitems= order.cart_items.count()
                
                # Check for existing refund requests
                order_refund_count = WalletRefund.objects.filter(order=order).count()
                product_refund_count = WalletRefund.objects.filter(order=order, product=product).count()
                
                order_product = order.cart_items.filter(id=cart_item_id)
                if  order_product.exists():
                    product = order_product.get(id=cart_item_id)
                    if WalletRefund.objects.filter(order=order).exists():
                        order_refund_request = WalletRefund.objects.filter(order=order).count()
                        if (order_refund_count > number_of_cartitems) or (product_refund_request > order_product.count()):
                            return RefundRequest(status= False, message="Already refunded for that product")
    
                refund_request = WalletRefund.objects.create(
                   order=order,
                   account_number=account_number,
                   product=product,
                   bank_name=bank_name,
                   number_of_product=number_of_product
               )

                return RefundRequest(status= True, message="Refund in progress", refund=refund_request)   
                
        except Exception as e:
            return RefundRequest(status= False, message=e)   


class ForceRefund(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String(required=True)
        refund_id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, token, refund_id):
        auth = authenticate_user(token)
        if not auth["status"]:
            return ForceRefund(status=auth["status"], message=auth["message"])

        try:
            # Check if the refund_id is valid and corresponds to a WalletRefund object
            if not refund_id:
                return ForceRefund(status=False, message="Invalid refund ID")

            refund_item = WalletRefund.objects.filter(id=refund_id).first()
            if not refund_item:
                return ForceRefund(status=False, message="Refund does not exist")

            if not refund_item.status:
                refunded_item = CartItem.objects.filter(
                    id=refund_item.product.id
                ).first()
                if not refunded_item:
                    return ForceRefund(status=False, message="Cart item does not exist")

                refunded_item_seller = Product.objects.filter(
                    id=refunded_item.product.id
                ).first()
                if not refunded_item_seller or not refunded_item_seller.user:
                    return ForceRefund(status=False, message="Seller does not exist")

                item_price = round(
                    refunded_item.price * refund_item.number_of_product, 2
                )
                seller_wallet = Wallet.objects.filter(
                    owner=refunded_item_seller.user.id
                ).first()
                if not seller_wallet:
                    return ForceRefund(
                        status=False, message="Seller wallet does not exist"
                    )

                seller_wallet.balance -= item_price
                seller_wallet.save()
                refund_item.status = True
                refund_item.save()

                return ForceRefund(
                    status=True,
                    message="Amount successfully deducted from seller's wallet",
                )
            else:
                return ForceRefund(status=False, message="Already refunded")
        except Exception as e:
            return ForceRefund(status=False, message=str(e))
