import time as timex
import uuid
from datetime import time, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth.hashers import make_password
from django.db.models import F, Q, Sum
from django.utils import timezone

from market.models import CartItem
from users.models import ExtendUser, SellerCustomer, SellerProfile
from wallet.models import Wallet, WalletTransaction

from .models import *

sched = BackgroundScheduler(daemon=True)


def unpromote():
    from datetime import datetime

    now = timezone.now()  # now = datetime.now()
    filter = Q(promo__end_date__lte=now) | Q(promo__balance__lte=1)
    all_products = Product.objects.filter(filter, promoted=True)
    print("expired promotions", all_products)
    for product in all_products:
        seller_wallet = Wallet.objects.get(
            owner=ExtendUser.objects.get(id=product.user.id)
        )
        Product.objects.filter(id=product.id).update(promoted=False)
        active_promos = ProductPromotion.objects.filter(
            product=product, active=True, balance__gte=1
        )
        for pr in active_promos:
            if not pr.is_admin:
                sb = seller_wallet.balance
                seller_wallet.balance = sb + pr.balance
                seller_wallet.save()
            pr.balance = 0
            pr.save()
        ProductPromotion.objects.filter(product=product).update(active=False)


def completeDelivery():
    print("started completeDelivery")

    random_password = uuid.uuid4().hex  # This will generate a random string
    admin_email = "kwekadmin@admin.com"

    # Get or create the admin user
    admin_user, created = ExtendUser.objects.get_or_create(
        email=admin_email,
        defaults={
            "username": "kwekadmin",  # Or any other default username you want to set
            "full_name": "Kwek Admin",  # Adjust as needed
            "password": make_password(random_password),  # Set hashed password
            "is_admin": True,
            "is_staff": True,
            "is_verified": True,
        },
    )

    admin_wallet, _ = Wallet.objects.get_or_create(owner=admin_user)

    # Get the date 7 days ago
    # seven_days_ago = timezone.now() - timedelta(days=1)
    seven_days_ago = timezone.now() - timedelta(minutes=1)
    # TODO: put back to 7days

    # Use select_related to reduce the number of queries on related objects
    closed_orders = Order.objects.filter(
        closed=True,
        delivery_status="delivered",
        paid=True,
        disbursed_to_wallet=False,
        delivered_at__lt=seven_days_ago,  # more than 7 days ago
    ).prefetch_related(
        "cart_items__product__user"
    )  # Prefetch the product and related user

    # print(closed_orders)

    # Create a dictionary to store total price for each seller to update the wallet balance in bulk
    seller_wallet_updates = {}
    w_transactions = []
    total_charges = 0

    # Iterate over the closed orders
    for order in closed_orders:
        # Prefetch all the cart items for the order in one go
        cart_items = order.cart_items.all()

        # Process each cart item
        for item in cart_items:
            seller = item.product.user

            if not SellerProfile.objects.filter(user=seller).exists():
                continue
            seller_profile = SellerProfile.objects.get(user=seller)
            wallet = Wallet.objects.get(owner=seller)

            # Calculate the price for the cart item
            charge = item.quantity * item.charge
            price = (item.quantity * item.price) - charge

            # Update seller's wallet balance in memory (add up the balance for each seller)
            if seller in seller_wallet_updates:
                seller_wallet_updates[seller] += price
            else:
                seller_wallet_updates[seller] = price

            total_charges += charge

            w_transactions.append(
                WalletTransaction(
                    wallet=wallet,
                    amount=price,
                    remark=f"Purchase of {item.product.product_title} with id {item.product.id}",
                    status=True,
                    transaction_type="Product Purchase",
                )
            )

            w_transactions.append(
                WalletTransaction(
                    wallet=admin_wallet,
                    amount=charge,
                    remark=f"Purchase of {item.product.product_title} with id {item.product.id}",
                    status=True,
                    transaction_type="Product Purchase",
                )
            )

            # Update seller's customer list using get_or_create for efficiency
            seller_customer, _ = SellerCustomer.objects.get_or_create(
                seller=seller_profile
            )

            # Check if the buyer (order.user) is already in the customers_id list
            if order.user.id not in seller_customer.customer_id:
                seller_customer.customer_id.append(order.user.id)
                seller_customer.save()

    # Perform bulk wallet updates in one go
    for seller, total_price in seller_wallet_updates.items():
        Wallet.objects.filter(owner=seller).update(balance=F("balance") + total_price)

    admin_wallet.balance += total_charges
    admin_wallet.save()

    closed_orders.update(disbursed_to_wallet=True)
    WalletTransaction.objects.bulk_create(w_transactions)
    print("finished completeDelivery")


def keepAlive():
    print("keeping alive")
    timex.sleep(30)
    print("done keeping alive")


def start_market_jobs_scheduler():
    #timex.sleep(60)
    print("starting jobs scheduler !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    sched = BackgroundScheduler()
    sched.add_job(unpromote, "interval", minutes=10)
    sched.add_job(completeDelivery, "interval", minutes=10)
    sched.add_job(keepAlive, "interval", seconds=30)
    sched.start()
    print("started jobs scheduler !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
