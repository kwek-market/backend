import graphene
from datetime import timedelta, datetime
from users.sendmail import send_coupon_code
from users.validate import authenticate_user, authenticate_admin

from market.pusher import SendEmailNotification, push_to_client
from notifications.models import Message, Notification
from users.models import ExtendUser, SellerCustomer
from .models import Billing, Coupon, CouponUser, Payment, Pickup, Order, OrderProgress
from .object_types import BillingType, CouponType, PaymentType, PickupType
from .flutterwave import get_payment_url, verify_transaction
from market.models import (
    Cart,
    CartItem,
    Product,
    ProductOption,
    ProductPromotion,
    Sales,
    get_delivery_fee,
)
import uuid


class BillingAddress(graphene.Mutation):
    billing_address = graphene.Field(BillingType)
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        full_name = graphene.String(required=True)
        contact = graphene.String(required=True)
        address = graphene.String(required=True)
        state = graphene.String(required=True)
        city = graphene.String(required=True)
        token = graphene.String()

    @staticmethod
    def mutate(self, root, full_name, contact, address, state, city, token=None):
        billing_address = Billing.objects.filter(
            full_name=full_name,
            contact=contact,
            address=address,
            state=state,
            city=city,
        )
        if billing_address.exists():
            billing_address = Billing.objects.get(
                full_name=full_name,
                contact=contact,
                address=address,
                state=state,
                city=city,
            )
            return BillingAddress(
                billing_address=billing_address, status=True, message="Address added"
            )
        else:
            if token is None:
                billing_address = Billing.objects.create(
                    full_name=full_name,
                    contact=contact,
                    address=address,
                    state=state,
                    city=city,
                )
                return BillingAddress(
                    billing_address=billing_address,
                    status=True,
                    message="Address added",
                )
            elif token is not None:
                auth = authenticate_user(token)
                if not auth["status"]:
                    return BillingAddress(auth["status"], auth["message"])
                else:
                    user = auth["user"]
                    if user:
                        billing_address = Billing.objects.create(
                            full_name=full_name,
                            contact=contact,
                            address=address,
                            state=state,
                            city=city,
                            user=user,
                        )
                        return BillingAddress(
                            billing_address=billing_address,
                            status=True,
                            message="Address added",
                        )

                    else:
                        return BillingAddress(status=False, message="Invalid User")
            else:
                return BillingAddress(status=False, message="Address not added")


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
        address = Billing.objects.filter(id=address_id)

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

    @staticmethod
    def mutate(self, info, amount, token, description, redirect_url, currency="NGN"):
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
                        )
                        if link["status"] == True:
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
                    return PickupLocationDelete(status=False, message="Invalid amount")
            else:
                return PaymentInitiate(status=False, message="Invalid user")


class PaymentVerification(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    transaction_info = graphene.String()

    class Arguments:
        transaction_id = graphene.Int(required=True)
        payment_ref = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, transaction_id, payment_ref):
        try:
            verify = verify_transaction(transaction_id)
            if verify["status"] == True:
                Payment.objects.filter(ref=payment_ref).update(verified=True)
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
            return PaymentVerification(status=verify["status"], message=e)


class PlaceOrder(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    order_id = graphene.String()

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
        state,
        city="",
        coupon_ids=None,
        payment_ref=None,
    ):
        auth = authenticate_user(token)
        if not auth["status"]:
            return PlaceOrder(status=auth["status"], message=auth["message"])
        else:
            order = {}
            user = auth["user"]
            cart = Cart.objects.get(id=cart_id)
            cart_owner = cart.user
            cart_items = CartItem.objects.filter(cart=cart, ordered=False)
            for cart_item in cart_items:
                cart_item.check_and_update_quantity()
            cart_items = CartItem.objects.filter(cart=cart, ordered=False)
            if delivery_method == "door step":
                shipping_address = Billing.objects.get(id=address_id)
            elif delivery_method == "pickup":
                shipping_address = Pickup.objects.get(id=address_id)

            delivery_fee = get_delivery_fee(state.lower(), city.lower())

            if not user: return PlaceOrder(status=False, message="User does not exist")

            if not cart: return PlaceOrder(status=False, message="Cart does not exist")

            if user != cart_owner: return PlaceOrder(status=False, message="User is not the owner of the cart")


            try:

                if (payment_method != "pay on delivery"and payment_ref is None):
                    return PlaceOrder(
                        status=False,
                        message="Payment reference not provided",
                    )
            
                if (payment_method != "pay on delivery" and payment_ref is not None):
                    if not Payment.objects.filter(ref=payment_ref).exists: return PlaceOrder(
                            status=False,
                            message="Invalid payment reference",
                        )
                    
                    payment = Payment.objects.get(ref=payment_ref)
                    if payment.verified and payment.used: return PlaceOrder(
                                status=False,
                                message="Payment reference already used",)
                    
                    if not payment.verified :return PlaceOrder(
                            status=False,
                            message="Payment has not been verified",
                        )
                    
                coupons = []
                if coupon_ids:
                    for id in coupon_ids:
                        coupon = Coupon.objects.get(id=id)
                        if CouponUser.objects.get(coupon=coupon, user=user).exists(): coupons.append(id)              

                if coupon_ids and len(coupons) == 0: return PlaceOrder(status=False,message="No coupon applied",)

                order = Order.objects.create(
                            user=user,
                            payment_method=payment_method,
                            delivery_method=delivery_method,
                            coupon=coupons,
                            delivery_fee=delivery_fee,
                        )

                if delivery_method == "door step":
                    Order.objects.filter(id=order.id).update(
                        door_step=shipping_address
                    )
                elif delivery_method == "pickup":
                    Order.objects.filter(id=order.id).update(
                        pickup=shipping_address
                    )
                OrderProgress.objects.create(order=order)
                for cart_item in cart_items:
                    cart_item_quantity = cart_item.quantity
                    product = ProductOption.objects.get(id=cart_item.product_option_id)
                    product_quantity = product.quantity
                    for i in range(int(product_quantity)):
                        Sales.objects.create(
                            product=product.product,
                            amount=cart_item.price,
                        )

                    new_quantity = int(product_quantity) - int(
                        cart_item_quantity
                    )
                    ProductOption.objects.filter(id=id).update(
                        quantity=new_quantity
                    )
                    if ProductPromotion.objects.filter(
                        product=product.product, active=True
                    ).exists():
                        reach = (
                            ProductPromotion.objects.get(
                                product=product.product
                            ).reach
                            + 1
                        )
                        ProductPromotion.objects.filter(
                            product=cart_item.product
                        ).update(reach=reach)
                if payment_ref:
                    Payment.objects.filter(ref=payment_ref).update(
                        used=True
                    )
                    Order.objects.filter(id=order.id).update(paid=True)
                if Notification.objects.filter(user=user).exists():
                    notification = Notification.objects.get(user=user)
                else:
                    notification = Notification.objects.create(user=user)
                notification_message = Message.objects.create(
                    notification=notification,
                    message=f"Your order has been placed successfully",
                    subject="Order placed",
                )
                # print(notification_message.message)
                notification_info = {
                    "notification": str(
                        notification_message.notification.id
                    ),
                    "message": notification_message.message,
                    "subject": notification_message.subject,
                }
                push_to_client(user.id, notification_info)
                email_send = SendEmailNotification(user.email)
                email_send.send_only_one_paragraph(
                    notification_message.subject,
                    notification_message.message,
                )
                for seller_item in cart_items:
                    cart_item_seller = seller_item.product.user
                    if Notification.objects.filter(
                        user=cart_item_seller
                    ).exists():
                        notification = Notification.objects.get(
                            user=cart_item_seller
                        )
                    else:
                        notification = Notification.objects.create(
                            user=cart_item_seller
                        )
                    notification_message = Message.objects.create(
                        notification=notification,
                        message=f"You've got a new order - Order no. #{order.order_id}",
                        subject="New Order",
                    )
                    # print(notification_message.message)
                    notification_info = {
                        "notification": str(
                            notification_message.notification.id
                        ),
                        "message": notification_message.message,
                        "subject": notification_message.subject,
                    }
                    push_to_client(cart_item_seller.id, notification_info)
                    email_send = SendEmailNotification(
                        cart_item_seller.email
                    )
                    email_send.send_only_one_paragraph(
                        notification_message.subject,
                        notification_message.message,
                    )
                return PlaceOrder(
                    status=True,
                    message="Order placed successfully",
                    order_id=order.order_id,
                )
            except Exception as e:
                return PlaceOrder(status=False, message=e)






class TrackOrder(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        order_id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, order_id):
        if Order.objects.filter(order_id=order_id):
            try:
                order = Order.objects.get(order_id=order_id)
                order_progress = OrderProgress.objects.get(order=order)

                return TrackOrder(status=True, message=order_progress.progress)
            except Exception as e:
                return TrackOrder(status=False, message=e)
        else:
            return TrackOrder(status=False, message="Invalid Order id")


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
                OrderProgress.objects.filter(order=order).update(progress=progress)
                order_progress = OrderProgress.objects.get(order=order)

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
    def mutate(self, info, order_id, delivery_status):
        if Order.objects.filter(id=order_id).exists():
            try:
                Order.objects.filter(id=order_id).update(
                    delivery_status=delivery_status
                )
                order = Order.objects.get(id=order_id)
                if order.delivery_status == "delivered":
                    OrderProgress.objects.filter(order=order).update(
                        progress="Order Delivered"
                    )
                    Order.objects.filter(id=order_id).update(closed=True, paid=True)
                    for item_id in order.cart_items.all():
                        item = CartItem.objects.get(id=item_id)
                        seller = item.product.user
                        if SellerCustomer.objects.filter(seller=seller).exists():
                            customers_id = SellerCustomer.objects.get(
                                seller=seller
                            ).customer_id
                            if order.user.id in customers_id:
                                pass
                            else:
                                customers_id.append(order.user.id)
                                SellerCustomer.objects.filter(seller=seller).update(
                                    customer_id=customers_id
                                )
                    if Notification.objects.filter(user=order.user).exists():
                        notification = Notification.objects.get(user=order.user)
                    else:
                        notification = Notification.objects.create(user=order.user)
                    notification_message = Message.objects.create(
                        notification=notification,
                        message=f"Your order has been delivered successfully",
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
                return UpdateDeliverystatus(
                    status=True, message="Delivery status updated"
                )
            except Exception as e:
                return UpdateDeliverystatus(status=False, message=e)
        else:
            return UpdateDeliverystatus(status=False, message="Invalid Order Id")


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
                        notification = Notification.objects.get(
                            user=cart_item_seller
                        )
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
                send_coupon_code(emails, coupon.code,str(coupon.value))
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
        else:
            user = auth["user"]
            if user:
                try:
                    coupon = Coupon.objects.get(id=coupon_id)
                except Coupon.DoesNotExist:
                    return DeleteCoupon(status=False, message="Coupon does not exist")
                try:
                    CouponUser.objects.filter(coupon=coupon).delete()
                    return DeleteCoupon(
                        status=True, message="Coupon unapplied", coupon=coupon
                    )
                except Exception as e:
                    return DeleteCoupon(status=False, message=e)
