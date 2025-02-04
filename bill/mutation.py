import uuid
from datetime import datetime, timedelta

import graphene
from django.db import transaction
from django.utils import timezone
import logging
from market.models import (
    Cart,
    CartItem,
    Product,
    ProductOption,
    ProductPromotion,
    Sales,
    get_delivery_fee,
)
from market.pusher import SendEmailNotification, push_to_client
from notifications.models import Message, Notification
from users.models import ExtendUser, SellerCustomer, SellerProfile
from users.sendmail import send_coupon_code
from users.validate import authenticate_admin, authenticate_user
from wallet.models import Wallet

from .models import Billing, Coupon, CouponUser, Order, OrderProgress, Payment, Pickup
from .object_types import BillingType, CouponType, PaymentType, PickupType
from .payment import get_payment_url, verify_transaction

logger = logging.getLogger(__name__)

class BillingAddress(graphene.Mutation):
    billing_address = graphene.Field(BillingType)
    status = graphene.Boolean(default_value=False)
    message = graphene.String(default_value="")

    class Arguments:
        full_name = graphene.String(required=True)
        contact = graphene.String(required=True)
        address = graphene.String(required=True)
        state = graphene.String(required=True)
        city = graphene.String(required=True)
        token = graphene.String(required=False)

    @classmethod
    def mutate(cls, root, info, **kwargs) -> "BillingAddress":
        try:
            full_name = kwargs.get("full_name")
            contact = kwargs.get("contact")
            address = kwargs.get("address")
            state = kwargs.get("state")
            city = kwargs.get("city")
            token = kwargs.get("token")

            # Validate required fields
            if not all([full_name, contact, address, state, city]):
                return cls(status=False, message="All fields are required")

            # Check for existing address
            existing_address = Billing.objects.filter(
                full_name=full_name,
                contact=contact,
                address=address,
                state=state,
                city=city,
            ).first()

            if existing_address:
                return cls(
                    billing_address=existing_address,
                    status=True,
                    message="Address retrieved",
                )

            # Handle token authentication
            user = None
            if token:
                auth_result = authenticate_user(token)
                if not auth_result.get("status"):
                    return cls(
                        status=False,
                        message=auth_result.get("message", "Authentication failed"),
                    )
                user = auth_result.get("user")
                if not user:
                    return cls(status=False, message="Invalid User")

            # Create new billing address
            billing_data = {
                "full_name": full_name,
                "contact": contact,
                "address": address,
                "state": state,
                "city": city,
            }
            if user:
                billing_data["user"] = user

            billing_address = Billing.objects.create(**billing_data)

            return cls(
                billing_address=billing_address, status=True, message="Address added"
            )

        except Exception as e:
            return cls(status=False, message=f"Error: {str(e)}")


class BillingAddressUpdate(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    billing = graphene.Field(BillingType)

    class Arguments:
        address_id = graphene.String(required=True)
        full_name = graphene.String()
        contact = graphene.String()
        address = graphene.String()
        state = graphene.String()
        city = graphene.String()

    @staticmethod
    def mutate(
        self,
        info,
        address_id,
        full_name=None,
        contact=None,
        address=None,
        state=None,
        city=None,
    ):
        if Billing.objects.filter(id=address_id).exists():
            billing_address = Billing.objects.get(id=address_id)
            if full_name:
                fullname = full_name
            else:
                fullname = billing_address.full_name
            if contact:
                new_contact = contact
            else:
                new_contact = billing_address.contact
            if address:
                new_address = address
            else:
                new_address = billing_address.address
            if state:
                new_state = state
            else:
                new_state = billing_address.state
            if city:
                new_city = city
            else:
                new_city = billing_address.city
            try:
                billing = Billing.objects.filter(id=address_id).update(
                    full_name=fullname,
                    contact=new_contact,
                    address=new_address,
                    state=new_state,
                    city=new_city,
                )
                return BillingAddressUpdate(
                    status=True, message="Address updated successfully", billing=billing
                )
            except Exception as e:
                return BillingAddressUpdate(status=False, message=e)
        else:
            return BillingAddressUpdate(status=False, message="Invalid address id")


class BillingAddressDelete(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        address_id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, address_id):
        address = Billing.objects.filter(id=address_id)

        if address.exists():
            address.delete()
            return BillingAddressDelete(
                status=True, message="Address deleted successfully"
            )
        else:
            return BillingAddressDelete(status=False, message="Invalid address")


class PickUpLocation(graphene.Mutation):
    location = graphene.Field(PickupType)
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        contact = graphene.String(required=True)
        address = graphene.String(required=True)
        state = graphene.String(required=True)
        city = graphene.String(required=True)

    @staticmethod
    def mutate(self, root, name, contact, address, state, city):
        location = Pickup.objects.filter(name=name)
        if location.exists():
            return PickUpLocation(
                status=False, message=f"Location {name} already exists"
            )
        else:
            try:
                location = Pickup.objects.create(
                    name=name, contact=contact, address=address, state=state, city=city
                )
                return PickUpLocation(
                    location=location, status=True, message="Location added"
                )
            except Exception as e:
                return BillingAddressUpdate(status=False, message=e)


class PickupLocationUpdate(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arugments:
        address_id = graphene.String(required=True)
        name = graphene.String()
        contact = graphene.String()
        address = graphene.String()
        state = graphene.String()
        city = graphene.String()

    @staticmethod
    def mutate(
        self,
        info,
        address_id,
        name=None,
        contact=None,
        address=None,
        state=None,
        city=None,
    ):
        if Pickup.objects.filter(id=address_id).exists():
            pickup_address = Pickup.objects.get(id=address_id)
            if name:
                new_name = name
            else:
                new_name = pickup_address.name
            if contact:
                new_contact = contact
            else:
                new_contact = pickup_address.contact
            if address:
                new_address = address
            else:
                new_address = pickup_address.address
            if state:
                new_state = state
            else:
                new_state = pickup_address.state
            if city:
                new_city = city
            else:
                new_city = pickup_address.city
            try:
                pickup = Pickup.objects.filter(id=address_id).update(
                    name=new_name,
                    contact=new_contact,
                    address=new_address,
                    state=new_state,
                    city=new_city,
                )
                return PickupLocationUpdate(
                    status=True, message="Address updated successfully"
                )
            except Exception as e:
                return PickupLocationUpdate(status=False, message=e)
        else:
            return PickupLocationUpdate(status=False, message="Invalid address")


class PickupLocationDelete(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        address_id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, address_id):
        address = Pickup.objects.filter(id=address_id)

        if address.exists():
            address.delete()
            return PickupLocationDelete(
                status=True, message="Address deleted successfully"
            )
        else:
            return PickupLocationDelete(status=False, message="Invalid address")


class PaymentInitiate(graphene.Mutation):
    payment = graphene.Field(PaymentType)
    status = graphene.Boolean()
    message = graphene.String()
    payment_link = graphene.String()

    class Arguments:
        amount = graphene.Float(required=True)
        token = graphene.String(required=True)
        description = graphene.String(required=True)
        currency = graphene.String()
        redirect_url = graphene.String(required=True)
        gateway = graphene.String(required=True)

    @staticmethod
    def mutate(
        self,
        info,
        amount,
        token,
        description,
        redirect_url,
        currency="NGN",
        gateway="gateway",
    ):
        auth = authenticate_user(token)
        if not auth["status"]:
            return PaymentInitiate(status=auth["status"], message=auth["message"])
        else:
            if not redirect_url or redirect_url == "":
                return PaymentInitiate(
                    status=False, message="redirect url cannot be empty"
                )
            user = auth["user"]
            if user:
                if amount:
                    try:
                        payment = Payment.objects.create(
                            amount=amount,
                            user_id=user.id,
                            email=user.email,
                            name=user.full_name,
                            phone=user.phone_number,
                            description=description,
                            gateway=gateway,
                        )
                        if currency:
                            payment.currency = currency
                        payment.save()

                        link = get_payment_url(
                            user.id,
                            user.email,
                            user.full_name,
                            user.phone_number,
                            payment.ref,
                            float(amount),
                            payment.currency,
                            redirect_url,
                            payment.description,
                            gateway,
                        )
                        if link["status"] == True:
                            # solving edge case for paystack by replacing payment.ref
                            ref = link["reference"]
                            payment.ref = ref
                            payment.save()
                            return PaymentInitiate(
                                payment=payment,
                                status=True,
                                message=link["message"],
                                payment_link=link["payment_link"],
                            )
                        else:
                            return PaymentInitiate(
                                payment=payment,
                                status=False,
                                message=link["message"],
                                payment_link=link["payment_link"],
                            )
                    except Exception as e:
                        return PaymentInitiate(status=False, message=e)
                else:
                    return PaymentInitiate(status=False, message="Invalid amount")
            else:
                return PaymentInitiate(status=False, message="Invalid user")


class PaymentVerification(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    transaction_info = graphene.String()

    class Arguments:
        transaction_ref = graphene.String(required=True)
        transaction_id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, transaction_ref, transaction_id):
        try:
            if not Payment.objects.filter(ref=transaction_ref).exists():
                return PaymentVerification(
                    status=False,
                    message="payment not found",
                    transaction_info={},
                )

            payment = Payment.objects.get(ref=transaction_ref)
            trans_ref = transaction_ref
            if payment.gateway == "flutterwave":
                trans_ref = transaction_id

            verify = verify_transaction(trans_ref, payment.gateway)
            if verify["status"] == True:
                Payment.objects.filter(ref=transaction_ref).update(verified=True)
                return PaymentVerification(
                    status=verify["status"],
                    message=verify["message"],
                    transaction_info=verify["transaction_info"],
                )
            else:
                return PaymentVerification(
                    status=verify["status"],
                    message=verify["message"],
                    transaction_info=verify["transaction_info"],
                )
        except Exception as e:
            return PaymentVerification(status=False, message=e)


class PlaceOrder(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    order_id = graphene.String()
    id = graphene.String()

    class Arguments:
        token = graphene.String(required=True)
        cart_id = graphene.String(required=True)
        payment_method = graphene.String(required=True)
        delivery_method = graphene.String(required=True)
        address_id = graphene.String(required=True)
        payment_ref = graphene.String()
        coupon_ids = graphene.List(graphene.String)
        state = graphene.String(required=True)
        city = graphene.String()

    @staticmethod
    def mutate(
        self,
        info,
        token,
        cart_id,
        payment_method,
        delivery_method,
        address_id,
        state: str,
        city="",
        coupon_ids=None,
        payment_ref=None,
    ):
        # Authenticate user
        auth = authenticate_user(token)

        if not auth["status"]:
            return PlaceOrder(status=auth["status"], message=auth["message"])

        user = auth["user"]
        if not user:
            return PlaceOrder(status=False, message="User does not exist")

        # Validate cart
        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return PlaceOrder(status=False, message="Cart does not exist")

        # Ensure the user owns the cart
        if user != cart.user:
            return PlaceOrder(status=False, message="User is not the owner of the cart")

        # Validate cart items
        cart_items = CartItem.objects.filter(
            cart=cart, ordered=False
        ).check_and_update_items()
        if len(cart_items) < 1:
            return PlaceOrder(status=False, message="Cannot checkout empty cart")

        # Calculate total cart amount
        cart_items_amount = sum(
            cart_item.price * cart_item.quantity for cart_item in cart_items
        )

        # Validate delivery address
        try:
            if delivery_method == "door step":
                shipping_address = Billing.objects.get(id=address_id)
            elif delivery_method == "pickup":
                shipping_address = Pickup.objects.get(id=address_id)
        except (Billing.DoesNotExist, Pickup.DoesNotExist):
            return PlaceOrder(status=False, message="Invalid delivery address")

        # Calculate delivery fee
        delivery_fee = get_delivery_fee(state.lower(), city.lower())

        # Validate payment reference (if applicable)
        if payment_method != "pay on delivery":
            if not payment_ref:
                return PlaceOrder(
                    status=False, message="Payment reference not provided"
                )

            try:
                payment = Payment.objects.get(ref=payment_ref)
                if payment.used:
                    return PlaceOrder(
                        status=False, message="Payment reference already used"
                    )
                if not payment.verified:
                    return PlaceOrder(
                        status=False, message="Payment has not been verified"
                    )
                if payment.amount < cart_items_amount:
                    return PlaceOrder(status=False, message="Incomplete payment")
            except Payment.DoesNotExist:
                return PlaceOrder(status=False, message="Invalid payment reference")

        # Validate coupons
        coupons = []
        if coupon_ids:
            for coupon_id in coupon_ids:
                try:
                    coupon = Coupon.objects.get(id=coupon_id)
                    if CouponUser.objects.filter(coupon=coupon, user=user).exists():
                        coupons.append(coupon)
                except Coupon.DoesNotExist:
                    pass

            if not coupons:
                return PlaceOrder(status=False, message="No valid coupons applied")

        # Create order
        try:
            order = Order.objects.create(
                user=user,
                payment_method=payment_method,
                delivery_method=delivery_method,
                delivery_fee=delivery_fee,
                coupon=coupons if coupons else None,
            )

            # Associate cart items with the order
            for cart_item in cart_items:
                cart_item.ordered = True
                cart_item.save()
                order.cart_items.add(cart_item)

            # Associate delivery address with the order
            if delivery_method == "door step":
                order.door_step = shipping_address
            elif delivery_method == "pickup":
                order.pickup = shipping_address
            order.save()

            # Remove this line since OrderProgress is already created in OrderManager
            # OrderProgress.objects.create(order=order)  # <-- Remove this!

            # Handle payment reference (if applicable)
            if payment_ref:
                Payment.objects.filter(ref=payment_ref).update(used=True)
                order.paid = True
                order.save()

            # # Send notifications
            # send_order_notifications(user, order, cart_items)
            """ commented out till implemented and imported"""
            return PlaceOrder(
                status=True,
                message="Order placed successfully",
                order_id=order.order_id,
                id=order.id,
            )

        except Exception as e:
            return PlaceOrder(status=False, message=str(e))


class TrackOrder(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        order_id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
            order_progress = OrderProgress.objects.get(order=order)
            return TrackOrder(status=True, message=order_progress.progress)
        except Order.DoesNotExist:
            return TrackOrder(status=False, message="Invalid Order id")
        except OrderProgress.DoesNotExist:
            return TrackOrder(status=False, message="Order progress not found")
        except Exception as e:
            return TrackOrder(status=False, message=str(e))


class UpdateOrderProgress(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        order_id = graphene.String(required=True)
        progress = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, order_id, progress):
        if Order.objects.filter(id=order_id):
            try:
                order = Order.objects.get(id=order_id)
                order_progress = OrderProgress.objects.get(order=order)
                order_progress.progress = progress
                order_progress.save()

                return UpdateOrderProgress(status=True, message=order_progress.progress)
            except Exception as e:
                return UpdateOrderProgress(status=False, message=e)
        else:
            return UpdateOrderProgress(status=False, message="Invalid Order id")


class UpdateDeliverystatus(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        order_id = graphene.String(required=True)
        delivery_status = graphene.String(required=True)

    @staticmethod
    @transaction.atomic
    def mutate(self, info, order_id, delivery_status):
        if not Order.objects.filter(id=order_id).exists():
            return UpdateDeliverystatus(status=False, message="Invalid Order Id")

        try:
            with transaction.atomic():
                order = Order.objects.get(id=order_id)
                if (
                    delivery_status == "delivered"
                    and order.delivery_status == "delivered"
                ):
                    return UpdateDeliverystatus(
                        status=True, message="Delivery status already updated"
                    )

                # Update delivery status
                order.delivery_status = delivery_status
                order.save()

                # If the order is delivered, process seller payments and customer relationships
                if delivery_status == "delivered":
                    # Update order progress
                    order_progress = OrderProgress.objects.get(order=order)
                    order_progress.progress = "Order Delivered"
                    order_progress.save()

                    # Update order status
                    order.closed = True
                    order.paid = True
                    order.delivered_at = timezone.now()
                    order.save()

                    # Reduce product quantities and process seller updates
                    for cart_item in order.cart_items.all():
                        # Update product quantity
                        product_option = ProductOption.objects.get(
                            id=cart_item.product_option_id
                        )
                        product_option.quantity = max(
                            0, int(product_option.quantity) - cart_item.quantity
                        )
                        product_option.save()

                        seller = cart_item.product.user

                        # Update seller wallet - with validation
                        try:
                            seller_wallet = Wallet.objects.get(owner=seller)
                            price = cart_item.quantity * cart_item.price
                            seller_wallet.balance += price
                            seller_wallet.save()
                        except Wallet.DoesNotExist:
                            # Log the error and continue processing
                            logger.error(
                                f"Wallet not found for seller {seller.id}. Creating new wallet."
                            )
                            seller_wallet = Wallet.objects.create(
                                owner=seller,
                                balance=cart_item.quantity * cart_item.price,
                            )

                        # Update seller-customer relationship
                        try:
                            seller_profile = SellerProfile.objects.get(user=seller)
                            seller_customer, created = (
                                SellerCustomer.objects.get_or_create(
                                    seller=seller_profile
                                )
                            )

                            if not seller_customer.customer_id:
                                seller_customer.customer_id = []

                            if order.user.id not in seller_customer.customer_id:
                                seller_customer.customer_id.append(order.user.id)
                                seller_customer.save()
                        except SellerProfile.DoesNotExist:
                            logger.error(
                                f"SellerProfile not found for user {seller.id}"
                            )
                            continue

                    # Send notifications
                    try:
                        notification, created = Notification.objects.get_or_create(
                            user=order.user
                        )

                        notification_message = Message.objects.create(
                            notification=notification,
                            message="Your order has been delivered successfully",
                            subject="Order completed",
                        )
                        notification_info = {
                            "notification": str(notification_message.notification.id),
                            "message": notification_message.message,
                            "subject": notification_message.subject,
                        }
                        push_to_client(order.user.id, notification_info)

                        email_send = SendEmailNotification(order.user.email)
                        email_send.send_only_one_paragraph(
                            notification_message.subject, notification_message.message
                        )
                    except Exception as e:
                        logger.error(f"Failed to send notification: {str(e)}")

                return UpdateDeliverystatus(
                    status=True, message="Delivery status updated"
                )

        except Exception as e:
            logger.error(f"Error updating delivery status: {str(e)}")
            return UpdateDeliverystatus(
                status=False, message=f"Failed to update delivery status: {str(e)}"
            )


class CancelOrder(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        order_id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, order_id):
        if Order.objects.filter(id=order_id).exists():
            try:
                order = Order.objects.get(id=order_id)
                Order.objects.filter(id=order_id).update(closed=True)
                OrderProgress.objects.filter(order=order).update(
                    progress="Order cancelled"
                )
                if Notification.objects.filter(user=order.user).exists():
                    notification = Notification.objects.get(user=order.user)
                else:
                    notification = Notification.objects.create(user=order.user)
                notification_message = Message.objects.create(
                    notification=notification,
                    message=f"Your order has been cancelled successfully",
                    subject="Cancel order",
                )
                notification_info = {
                    "notification": str(notification_message.notification.id),
                    "message": notification_message.message,
                    "subject": notification_message.subject,
                }
                push_to_client(order.user.id, notification_info)
                email_send = SendEmailNotification(order.user.email)
                email_send.send_only_one_paragraph(
                    notification_message.subject, notification_message.message
                )
                for seller_item in order.cart_items.all():
                    # seller_item = CartItem.objects.get(id=item)
                    cart_item_seller = seller_item.product.user
                    if Notification.objects.filter(user=cart_item_seller).exists():
                        notification = Notification.objects.get(user=cart_item_seller)
                    else:
                        notification = Notification.objects.create(
                            user=cart_item_seller
                        )
                    notification_message = Message.objects.create(
                        notification=notification,
                        message=f"Order no. #{order.order_id} has been cancelled",
                        subject="Order Cancelled",
                    )
                    # print(notification_message.message)
                    notification_info = {
                        "notification": str(notification_message.notification.id),
                        "message": notification_message.message,
                        "subject": notification_message.subject,
                    }
                    push_to_client(cart_item_seller.id, notification_info)
                    email_send = SendEmailNotification(cart_item_seller.email)
                    email_send.send_only_one_paragraph(
                        notification_message.subject, notification_message.message
                    )
                return CancelOrder(status=True, message="Order cancelled")

            except Exception as e:
                return CancelOrder(status=False, message=e)
        else:
            return CancelOrder(status=False, message="Invalid order id")


class CreateCoupon(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    coupon = graphene.Field(CouponType)

    class Arguments:
        value = graphene.Int(required=True)
        code = graphene.String()
        days = graphene.Int()
        valid_until = graphene.DateTime()
        user_list = graphene.List(graphene.String)

    @staticmethod
    def mutate(
        self, info, value, code=None, days=None, valid_until=None, user_list=None
    ):
        if days and (not valid_until):
            valid_until_date = datetime.today() + timedelta(days=days)
        elif valid_until and (not days):
            valid_until_date = valid_until
        else:
            return CreateCoupon(
                status=False,
                message="Please enter either number of days(int) or valid_until(datetime)",
            )
        try:
            if code and user_list:
                coupon = Coupon.objects.create(
                    value=value,
                    valid_until=valid_until_date,
                    code=code,
                    user_list=user_list,
                )

                emails = ExtendUser.get_emails_by_ids(user_list)
                send_coupon_code(emails, coupon.code, str(coupon.value))
            elif user_list and (not code):
                coupon = Coupon.objects.create(
                    value=value, valid_until=valid_until_date, user_list=user_list
                )
                emails = ExtendUser.get_emails_by_ids(user_list)
                send_coupon_code(emails, coupon.code, str(coupon.value))
            elif code and (not user_list):
                coupon = Coupon.objects.create(
                    value=value, valid_until=valid_until_date, code=code
                )
            else:
                coupon = Coupon.objects.create(
                    value=value, valid_until=valid_until_date
                )
            return CreateCoupon(
                status=True, message="Coupon created successfully", coupon=coupon
            )
        except Exception as e:
            return CreateCoupon(status=False, message=e)


class ApplyCoupon(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    coupon = graphene.Field(CouponType)

    class Arguments:
        token = graphene.String(required=True)
        coupon_id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, token, coupon_id):
        auth = authenticate_user(token)
        if not auth["status"]:
            return ApplyCoupon(status=auth["status"], message=auth["message"])
        else:
            user = auth["user"]
        try:
            coupon = Coupon.objects.get(id=coupon_id)
        except Coupon.DoesNotExist:
            return ApplyCoupon(status=False, message="Coupon does not exist")

        if coupon.expired:
            return ApplyCoupon(status=False, message="Coupon is expired")

        elif coupon.user_list:
            if str(user.id) in coupon.user_list:
                if coupon.is_redeemed:
                    return ApplyCoupon(
                        status=False, message="Coupon has been redeemed by all users"
                    )
                else:
                    CouponUser.objects.create(coupon=coupon, user=user)

                    return ApplyCoupon(
                        status=True, message="Coupon redeemed", coupon=coupon
                    )
            else:
                return ApplyCoupon(
                    status=False, message="Coupon is not available for this user"
                )
        elif CouponUser.objects.filter(coupon=coupon, user=user).exists():
            return ApplyCoupon(
                status=False, message="This coupon has been redeemed by this user"
            )
        else:
            CouponUser.objects.create(coupon=coupon, user=user)

            return ApplyCoupon(status=True, message="Coupon redeemed", coupon=coupon)


class UnapplyCoupon(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    coupon = graphene.Field(CouponType)

    class Arguments:
        coupon_ids = graphene.List(graphene.String, required=True)
        token = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, token, coupon_ids):
        auth = authenticate_user(token)
        if not auth["status"]:
            return ApplyCoupon(status=auth["status"], message=auth["message"])
        else:
            user = auth["user"]

        for id in coupon_ids:
            try:
                coupon = Coupon.objects.get(id=id)
            except Coupon.DoesNotExist:
                return ApplyCoupon(status=False, message="Coupon does not exist")
            try:
                CouponUser.objects.filter(coupon=coupon, user=user).delete()
                return UnapplyCoupon(
                    status=True, message="Coupon unapplied", coupon=coupon
                )
            except Exception as e:
                return UnapplyCoupon(status=False, message=e)


class DeleteCoupon(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        coupon_id = graphene.String(required=True)
        token = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, token, coupon_id):
        auth = authenticate_admin(token)
        if not auth["status"]:
            return DeleteCoupon(status=auth["status"], message=auth["message"])

        user = auth["user"]
        if user:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                CouponUser.objects.filter(coupon=coupon).delete()
                coupon.delete()  # Also delete the coupon itself
                return DeleteCoupon(status=True, message="Coupon deleted successfully")
            except Coupon.DoesNotExist:
                return DeleteCoupon(status=False, message="Coupon does not exist")
            except Exception as e:
                return DeleteCoupon(status=False, message=str(e))

        return DeleteCoupon(status=False, message="Unauthorized")
