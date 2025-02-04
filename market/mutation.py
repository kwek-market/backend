from datetime import timedelta

import graphene
import jwt
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.db import transaction
from django.db.models import (BooleanField, Count, ExpressionWrapper, F,
                              FloatField, IntegerField, OuterRef, Prefetch, Q,
                              Subquery, TextField)
from django.utils import timezone

from notifications.models import Message, Notification
from users.models import ExtendUser
from users.validate import authenticate_admin, authenticate_user
from wallet.models import Wallet

from .models import *
from .object_types import *
from .post_offices import post_offices
from .pusher import *

# print(post_offices.get_all())
# print(post_offices.get_for_state("lagos"))
# print(post_offices.get_for_lga("surulere"))
# print(post_offices.get_for_state_and_lga("lagos","surulere"))


sched = BackgroundScheduler(daemon=True)
# =====================================================================================================================
# Product Input Arguments
class ProductInput(graphene.InputObjectType):
    id = graphene.String()
    product_title = graphene.String(required=True)
    brand = graphene.String()
    product_weight = graphene.String()
    short_description = graphene.String()
    charge_five_percent_vat = graphene.Boolean(required=True)
    return_policy = graphene.String()
    warranty = graphene.String()
    color = graphene.String()
    gender = graphene.String()
    keyword = graphene.List(graphene.String)
    clicks = graphene.Int()
    promoted = graphene.Boolean()
    category = graphene.String()
    subcategory = graphene.String()


# =====================================================================================================================
# Category Mutations
class AddCategory(graphene.Mutation):
    category = graphene.Field(CategoryType)
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        visibility = graphene.String(required=True)
        icon = graphene.String()
        publish_date = graphene.Date()
        parent = graphene.String()
    @staticmethod
    def mutate(self, info, name, visibility, parent=None, icon=None, publish_date=None):
        if Category.objects.filter(name=name).exists() and parent is None:
            return AddCategory(status=False,message="Category already exists")
        else:      
            try:
                if parent is None:
                    if icon is None:
                        return AddCategory(status=False,message="Icon is required for Category")
                    category = Category.objects.create(name=name, visibility=visibility, publish_date=publish_date, icon=icon)
                    return AddCategory(
                        category=category,
                        status=True,
                        message="Category added successfully"
                    )
                else:
                    if Category.objects.filter(name=parent).exists():
                        parent = Category.objects.get(name=parent)
                        category = Category.objects.create(name=name, parent=parent, visibility=visibility,  publish_date=publish_date, icon=icon)
                        return AddCategory(
                            category=category,
                            status=True,
                            message="Subcategory added successfully"
                        )
                    else:
                        return AddCategory(status=False,message="Parent category does not exist")
            except Exception as e:
                return AddCategory(status=False,message=e)

class UpdateCategory(graphene.Mutation):
    message = graphene.String()
    category = graphene.Field(CategoryType)
    status = graphene.Boolean()

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String(required=True)
        visibility = graphene.String()
        publish_date = graphene.Date()
        parent = graphene.String()
        icon = graphene.String()

    @staticmethod
    def mutate(self, info, name=None, parent=None, icon=None, id=None, visibility=None, publish_date=None):
        try:
            if Category.objects.filter(id=id).exists():
                updated_fields = {}

                if icon is not None:
                    updated_fields['icon'] = icon

                if name is not None:
                    updated_fields['name'] = name
                    # category = Category.objects.filter(id=id).update(name=name)
                    # UpdateCategory(category=category, status=True)
                if parent is not None:
                    updated_fields['parent'] = parent
                    # category = Category.objects.filter(id=id).update(parent=parent)
                    # UpdateCategory(category=category, status=True)
                if visibility is not None:
                    updated_fields['visibility'] = visibility
                    # category = Category.objects.filter(id=id).update(visibility=visibility)
                    # UpdateCategory(category=category, status=True)
                if publish_date is not None:
                    updated_fields['publish_date'] = publish_date
                    # category = Category.objects.filter(id=id).update(publish_date=publish_date)
                    # UpdateCategory(category=category, status=True)
                # else:
                #     return UpdateCategory(status=False,message="Invalid name or parent or visibility")
                    
                if updated_fields:
                    try:
                        category = Category.objects.filter(id=id).update(**updated_fields)
                        return UpdateCategory(status=True, message="Category updated successfully")
                    except Exception as e:
                        return UpdateCategory(status=False, message=e)
                else:
                    return UpdateCategory(status=False, message="No valid fields to update")
                       
            else:
                return UpdateCategory(status=False,message="Invalid id")
            # return UpdateCategory(status=True, message="Successfully Updated")
        except Exception as e:
            return UpdateCategory(status=False,message=e)


class DeleteCategory(graphene.Mutation):
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, id):
        try:
            if Category.objects.filter(id=id).exists():
                Category.objects.filter(id=id).delete()
                return DeleteCategory(
                    status = True,
                    message = "Deleted successfully"
                )
            else:
                return DeleteCategory(status=False,message="Invalid id")
        except Exception as e:
            return DeleteCategory(status=False,message=e)
# =====================================================================================================================

# Product Mutations
class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String(required=True)
        product_title = graphene.String(required=True)
        category = graphene.String(required=True)
        subcategory = graphene.String(required=True)
        brand = graphene.String()
        product_weight = graphene.String()
        product_image_url = graphene.List(graphene.String, required=True)
        short_description = graphene.String()
        charge_five_percent_vat = graphene.Boolean(required=True)
        return_policy = graphene.String()
        warranty = graphene.String()
        product_options = graphene.List(graphene.String, required=True)
        color = graphene.String()
        gender = graphene.String()
        keyword = graphene.List(graphene.String)


    @staticmethod
    def mutate(
        self,
        info,
        token, 
        product_title,
        category,
        charge_five_percent_vat,
        keyword,
        subcategory,
        product_image_url,
        product_options,
        brand="",
        product_weight="",
        short_description="",
        return_policy="",
        warranty="",
        color="",
        gender=""
    ):
        auth = authenticate_user(token)
        if not auth["status"]:
            return CreateProduct(status=auth["status"],message=auth["message"])
        user = auth["user"]

        if not Category.objects.filter(id=category).exists:
            return CreateProduct(
            status=False,
            message="category not found"
            )

        p_cat = Category.objects.get(id=category)

        if not Category.objects.filter(id=subcategory).exists:
            return CreateProduct(
            status=False,
            message="sub category not found"
            )
        
        sub_cat = Category.objects.get(id=subcategory)
        

        for word in keyword:
            if not Keyword.objects.filter(keyword=word).exists():
                Keyword.objects.create(keyword=word)

        product = Product.objects.create(
            keyword=keyword,
            product_title=product_title,
            user=user,
            category=p_cat,
            subcategory=sub_cat,
            brand=brand,
            product_weight=product_weight,
            short_description=short_description,
            charge_five_percent_vat=charge_five_percent_vat,
            return_policy=return_policy,
            warranty=warranty,
            color=color,
            gender=gender
        )

        for url in product_image_url:
            ProductImage.objects.create(product=product, image_url=url)
        for item in product_options:
            option = eval(item)
            keys = option.keys()

            size = "" if "size" not in keys else option["size"]
            color = "" if "color" not in keys else option["color"]
            quantity = "" if "quantity" not in keys else option["quantity"]
            price = "" if "price" not in keys else option["price"]
            discounted_price = "" if "discounted_price" not in keys else option["discounted_price"]
            option_total_price = 0.0
            newoption = ProductOption.objects.create(product=product, size=size,color=color, quantity=quantity, price=price, discounted_price=discounted_price, option_total_price=option_total_price)

        
        if Notification.objects.filter(user=product.user).exists():
            notification = Notification.objects.get(user=product.user)
        else:
            notification = Notification.objects.create(
                user=product.user
            )
        notification_message = Message.objects.create(
            notification=notification,
            message=f"A new product {product.product_title}, has been added to your store.",
            subject="New Product"
        )
        notification_info = {"notification":str(notification_message.notification.id),
                "message":notification_message.message, 
                "subject":notification_message.subject}
        push_to_client(product.user.id, notification_info)
        email_send = SendEmailNotification(user.email)
        email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)
        return CreateProduct(
            product=product,
            status=True,
            message="Product added"
        )


class ProductClick(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String(required=False)
        product_id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info,product_id, token=None):
        product = Product.objects.get(id=product_id)
        if product:
            if product.promoted:
                promos = ProductPromotion.objects.filter(product=product, active=True)
                # ProductPromotion.objects.filter(product=product, active=True).update(link_clicks=F('link_clicks')+1)
                print(promos)
                for pr in promos:
                    c_clicks, active = pr.link_clicks +1, True
                    c_balance = pr.balance

                    if pr.balance > 0:
                        c_balance = c_balance - settings.PROMOTION_CLICK_CHARGE
                    elif pr.is_admin:
                        c_balance = pr.balance
                    else:
                        c_balance = c_balance - settings.PROMOTION_CLICK_CHARGE

                    if c_balance <= 0 and not pr.is_admin:
                        c_balance, active = 0, False
                    pr.link_clicks, pr.balance, pr.active =c_clicks, c_balance, active
                    pr.save()
                if ProductPromotion.objects.filter(product=product, active=True).count() < 1:
                    Product.objects.filter(id=product.id).update(promoted=False)
                          
            clicks = product.clicks + 1
            product.clicks = clicks
            product.save()
            return ProductClick(
                status = True,
                message = "Click added"
            )
        else:
            return ProductClick(status=False,message="Invalid Product")

class UpdateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String(required=True)
        product_id = graphene.String(required=True)
        charge_five_percent_vat = graphene.Boolean() 
        product_title = graphene.String()
        category = graphene.String()
        subcategory = graphene.String() 
        product_image_url = graphene.List(graphene.String)  
        product_options = graphene.List(graphene.String)
        keyword = graphene.List(graphene.String)
        brand = graphene.String()
        product_weight = graphene.String()
        short_description = graphene.String()
        return_policy = graphene.String()
        warranty = graphene.String()
        color = graphene.String()
        gender = graphene.String()

    @staticmethod
    def mutate(
        self,
        info,
        token, 
        product_id, 
        charge_five_percent_vat=None,
        product_title=None,
        category=None,
        subcategory=None,
        product_image_url=None,
        product_options=None,
        keyword=None,
        brand=None,
        product_weight=None,
        short_description=None,
        return_policy=None,
        warranty=None,
        color=None,
        gender=None
    ):
        try:
            with transaction.atomic():
                auth = authenticate_user(token)
                if not auth["status"]:
                    return UpdateProduct(status=auth["status"],message=auth["message"])
                user = auth["user"]

                if not Product.objects.filter(id=product_id).exists():
                    return UpdateProduct(status=False,message="product not found")
                
                product = Product.objects.get(id=product_id)

                if not user.is_admin and product.user.id != user.id:
                    return UpdateProduct(status=False,message="you are not allowed to update this product")
                
                if category:
                    if not Category.objects.filter(id=category).exists:
                        return UpdateProduct(
                        status=False,
                        message="category not found"
                        )
                    cate = Category.objects.get(id=category)
                    product.category = cate
                    
                
                if subcategory:
                    if not Category.objects.filter(id=subcategory).exists:
                        return UpdateProduct(
                                status=False,
                            message="sub category not found"
                            )
                    sub_cat = Category.objects.get(id=subcategory)
                    product.subcategory = sub_cat

                if keyword:
                    for word in keyword:
                        if not Keyword.objects.filter(keyword=word).exists():
                            Keyword.objects.create(keyword=word)
                    product.keyword = keyword


                if product_image_url:
                    ProductImage.objects.filter(product=product).delete()
                    for url in product_image_url:
                        ProductImage.objects.create(product=product, image_url=url)
                
                if product_options:
                    ProductOption.objects.filter(product=product).delete()
                    for item in product_options:
                        option = eval(item)
                        keys = option.keys()

                        size = "" if "size" not in keys else option["size"]
                        color = "" if "color" not in keys else option["color"]
                        quantity = "" if "quantity" not in keys else option["quantity"]
                        price = "" if "price" not in keys else option["price"]
                        discounted_price = "" if "discounted_price" not in keys else option["discounted_price"]
                        option_total_price = 0.0
                        ProductOption.objects.create(product=product, size=size,color=color, quantity=quantity, price=price, discounted_price=discounted_price, option_total_price=option_total_price)

                if product_title:
                    product.product_title=product_title

                if brand:
                    product.brand=brand

                if product_weight:
                    product.product_weight=product_weight

                if short_description:
                    product.short_description=short_description

                if charge_five_percent_vat:
                    product.charge_five_percent_vat=charge_five_percent_vat

                if return_policy:
                    product.return_policy=return_policy

                if warranty:
                    product.warranty=warranty

                if color:
                    product.color=color

                if gender:
                    product.gender=gender

                product.save()
            return UpdateProduct(status=True,message="update successful", product=product)
        except Exception as e:
            return UpdateProduct(status=False,message=e)

class DeleteProduct(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String(required=True)
        id = graphene.String(required=True)

    @staticmethod
    def mutate(
        self,
        info,
        token, 
        id,
    ):
        try:
            auth = authenticate_user(token)
            if not auth["status"]:
                return DeleteProduct(status=auth["status"],message=auth["message"])
            user = auth["user"]

            if not Product.objects.filter(id=id).exists():
                return DeleteProduct(status=False,message="product not found")
            
            product = Product.objects.get(id=id)

            if not user.is_admin and product.user.id != user.id:
                return DeleteProduct(status=False,message="you are not allowed to delete this product")
            
            product.delete()
            return DeleteProduct(status=True,message="delete successful")
        except Exception as e:
            return DeleteProduct(status=False,message=e)


# class UpdateProductMutation(graphene.Mutation):
#     product = graphene.Field(ProductType)

#     class Arguments:
#         id = graphene.Int(required=True)
#         product_data = ProductInput(required=True)


#     @staticmethod
#     def mutate(root, info, id=None, product_data=None):
#         product = Product.objects.filter(id=id)
#         product.update(**product_data)
#         return CreateProduct(product=product.first())
# =====================================================================================================================

# product rating
class Reviews(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    product_review=graphene.Field(RatingType)

    class Arguments:
        product_id = graphene.String()
        # comment = graphene.String()
        review_id = graphene.String()
        review = graphene.String()
        rating = graphene.Int()
        token = graphene.String()
        vote = graphene.String()
    
    @staticmethod
    def mutate(
        root,
        info,
        token,
        product_id=None,
        rating=None,
        review=None,
        review_id=None,
        vote=None
    ):
        auth = authenticate_user(token)
        if not auth["status"]:
            return Reviews(status=auth["status"],message=auth["message"])
        user = auth["user"]
        
        if product_id is not None:
            product = Product.objects.get(id=product_id)
        if review_id is not None and user:
            parent = Rating.objects.get(id=review_id)
            if parent and (review is not None):
                product_review = Rating.objects.create(
                    user=user,
                    review=review,
                    parent=parent
                )

                return Reviews(
                    product_review=product_review,
                    status=True,
                    message="Comment added successfully"
                )
            if parent and (vote is not None):
                if vote == "up":
                    product_review = Rating.objects.get(id=review_id)
                    likes = product_review.likes
                    likes += 1
                    product_review = Rating.objects.filter(id=review_id).update(likes=likes)
                    return Reviews(
                        product_review=product_review,
                        status=True,
                        message="Upvoted successfully"
                    )
                elif vote == "down":
                    product_review = Rating.objects.get(id=review_id)
                    dislikes = product_review.dislikes
                    dislikes += 1
                    product_review = Rating.objects.filter(id=review_id).update(dislikes=dislikes)
                    return Reviews(
                        product_review=product_review,
                        status=True,
                        message="Downvoted successfully"
                    )
                else:
                    return Reviews(status=False,message="Invalid Vote")
            
        
        if user:
            if product and (review is not None) and (rating is not None):
                product_review=Rating.objects.create(
                    user=user,
                    product=product,
                    rating=rating,
                    review=review
                )
                if Notification.objects.filter(user=product.user).exists():
                    notification = Notification.objects.get(user=product.user)
                else:
                    notification = Notification.objects.create(
                        user=product.user
                    )
                notification_message = Message.objects.create(
                    notification=notification,
                    message=f"A review has been added to your product {product.product_title}",
                    subject="New Review"
                )
                notification_info = {"notification":str(notification_message.notification.id),
                "message":notification_message.message, 
                "subject":notification_message.subject}
                push_to_client(product.user.id, notification_info)
                email_send = SendEmailNotification(user.email)
                email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)
                return Reviews(
                    product_review=product_review,
                    status=True,
                    message="Review and rating added successfully"
                )
            elif product and (review is not None):
                product_review=Rating.objects.create(
                    user=user,
                    product=product,
                    review=review
                )
                if Notification.objects.filter(user=product.user).exists():
                    notification = Notification.objects.get(user=product.user)
                else:
                    notification = Notification.objects.create(
                        user=product.user
                    )
                notification_message = Message.objects.create(
                    notification=notification,
                    message=f"A review has been added to your product {product.product_title}",
                    subject="New Review"
                )
                notification_info = {"notification":str(notification_message.notification.id),
                "message":notification_message.message, 
                "subject":notification_message.subject}
                push_to_client(product.user.id, notification_info)
                email_send = SendEmailNotification(user.email)
                email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)
                return Reviews(
                    product_review=product_review,
                    status=True,
                    message="Review added successfully"
                )
            elif product and (rating is not None):
                product_review=Rating.objects.create(
                    user=user,
                    product=product,
                    rating=rating
                )
                if Notification.objects.filter(user=product.user).exists():
                    notification = Notification.objects.get(user=product.user)
                else:
                    notification = Notification.objects.create(
                        user=product.user
                    )
                notification_message = Message.objects.create(
                    notification=notification,
                    message=f"A review has been added to your product {product.product_title}",
                    subject="New Review"
                )
                notification_info = {"notification":str(notification_message.notification.id),
                "message":notification_message.message, 
                "subject":notification_message.subject}
                push_to_client(product.user.id, notification_info)
                email_send = SendEmailNotification(user.email)
                email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)
                return Reviews(
                    product_review=product_review,
                    status=True,
                    message="Rating added successfully"
                )
            else:
                return Reviews(status=False,message="Invalid Product")
        else:
            return Reviews(status=False,message="Invalid user")

# Subscriber Mutation
class CreateSubscriber(graphene.Mutation):
    subscriber = graphene.Field(NewsletterType)
    message = graphene.String()
    status = graphene.Boolean()
    class Arguments:
        email = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, email):
        if Newsletter.objects.filter(email=email).exists():
            return CreateSubscriber(
                status=False, message="You have already subscribed")
        else:
            subscriber = Newsletter(email=email)
            subscriber.save()
        return CreateSubscriber(subscriber=subscriber,
                                        status=True,
                                        message="Subscription Successful")
# =====================================================================================================================

class ContactUs(graphene.Mutation):
    contact_message = graphene.Field(ContactMessageType)
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        email = graphene.String(required=True)
        name = graphene.String(required=True)
        message = graphene.String(required=True)
    
    @staticmethod
    def mutate(root, info, email, name, message):
        if ContactMessage.objects.filter(email=email, message=message).exists():
            return ContactUs(
                status=False, message="You have already sent this message")
        else:
            payload = {
            "email": "gregoflash05@gmail.com",
            "send_kwek_email": "",
            "product_name": "Support Kwek Market",
            "api_key": settings.PHPWEB,
            "from_email": settings.KWEK_EMAIL,
            "subject": "Contact us message from " + name,
            "event": "notification",
            "notification_title": "Contact us message from " + name,
            "no_html_content": message,
            "html_content": "",
            }
            try:
                status,email_message = send_email_through_PHP(payload)
                if status:
                    contacting = ContactMessage(email=email, name=name, message=message)
                    contacting.save()
                    return ContactUs(contact_message=contacting,status=True, message="message successfully sent")
                else:
                    return ContactUs(status=False, message="Error Occured, Try again later")
            except Exception as e:
                return ContactUs(status=False, message=e)


# Wishlist Mutation
class WishListMutation(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String()
        product_id = graphene.String()

    @staticmethod
    def mutate(self, info, product_id, token, is_check=False):
        auth = authenticate_user(token)
        if not auth["status"]:
            return WishListMutation(status=auth["status"],message=auth["message"])
        user = auth["user"]
        if user:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return WishListMutation(status=False,message="Product with product_id does not exist")

            try:
                user_wish = Wishlist.objects.get(user=user)
            except Exception:
                user_wish = Wishlist.objects.create(user=user)

            has_product = Wishlist.objects.filter(user=user, wishlist_item__product=product)

            if has_product:
                WishListItem.objects.filter(product=product).delete()
            else:
                WishListItem.objects.create(wishlist=user_wish, product=product)
            return WishListMutation(
                status = True,
                message = "Successful"
            )

# =====================================================================================================================

# Cart Mutation
class CreateCartItem(graphene.Mutation):
    cart_item = graphene.Field(CartType)
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String()
        ip_address = graphene.String()
        product_option_id = graphene.String(required=True)
        quantity = graphene.Int()

    @staticmethod
    def mutate(self, info, product_option_id, token=None, ip_address=None, quantity=1):
        try:
            option = ProductOption.objects.get(id=product_option_id)
        except Exception:
            return CreateCartItem(status=False,message="product option not found")
        discounted_price = option.get_product_discounted_price()
        price = option.get_product_price()
        charge = option.get_product_charge()
        product = Product.objects.get(options__id=product_option_id)
        if token:
            print("using token")
            auth = authenticate_user(token)
            if not auth["status"]:
                return CreateCartItem(status=auth["status"],message=auth["message"])
            user = auth["user"]
            if user:
                try:
                    user_cart = user.user_carts
                except Exception:
                    user_cart = Cart.objects.create(user=user)
                
                has_product = Cart.objects.filter(user=user, cart_item__product_option_id=product_option_id, cart_item__ordered=False)

                if has_product:
                    cart_item = CartItem.objects.get(cart__user=user, product_option_id=product_option_id, ordered=False)
                    quantity = int(cart_item.quantity) + quantity
                    cart_item = CartItem.objects.filter(id=cart_item.id, product=cart_item.product).update(quantity=quantity)
                    return CreateCartItem(
                        cart_item=cart_item,
                        status = True,
                        message = "Added to cart",
                    )
                else:
                    try:
                        if discounted_price > 0:
                            cart_item = CartItem.objects.create(product=product, quantity=quantity, price=discounted_price,charge=charge, cart=user_cart, product_option_id=product_option_id)
                        else:
                            if price <=0: charge = 0
                            cart_item = CartItem.objects.create(product=product, quantity=quantity, price=price,charge=charge, cart=user_cart, product_option_id=product_option_id)
                        return CreateCartItem(
                            cart_item=cart_item,
                            status = True,
                            message = "Added to cart",
        
                        )
                    except Exception as e:
                        return CreateCartItem(status=False,message=e)
        elif ip_address:
            try:
                user_cart = Cart.objects.get(ip=ip_address)
            except Exception:
                user_cart = Cart.objects.create(ip=ip_address)

            has_product = Cart.objects.filter(ip=ip_address, cart_item__product_option_id=product_option_id, cart_item__ordered=False)

            if has_product:
                cart_item = CartItem.objects.get(cart__ip=ip_address, product_option_id=product_option_id)
                quantity = int(cart_item.quantity) + quantity
                cart_item = CartItem.objects.filter(id=cart_item.id, product=cart_item.product).update(quantity=quantity)
                return CreateCartItem(
                    cart_item=cart_item,
                    status = True,
                    message = "Added to cart",
        
                )
            else:
                try:
                    if discounted_price > 0:
                        cart_item = CartItem.objects.create(product=product, quantity=quantity, price=discounted_price,charge=charge, cart=user_cart, product_option_id=product_option_id)
                    else:
                        if price <=0: charge = 0
                        cart_item = CartItem.objects.create(product=product, quantity=quantity, price=price,charge=charge, cart=user_cart, product_option_id=product_option_id)
                    return CreateCartItem(
                        cart_item=cart_item,
                        status = True,
                        message = "Added to cart",
                 
                    )
                except Exception as e:
                    return CreateCartItem(status=False,message=e)
        else:
            return CreateCartItem(status=False,message="Invalid user")

# =====================================================================================================================
class DeleteCart(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        cart_id = graphene.String(required=True)
        token = graphene.String()
        ip = graphene.String()

    def mutate(self, info, cart_id, token=None, ip=None):
        if token:
            auth = authenticate_user(token)
            if not auth["status"]:
                return DeleteCart(status=auth["status"],message=auth["message"])
            user = auth["user"]
            try:
                Cart.objects.filter(id=cart_id, user=user).delete()

                return DeleteCart(
                    status = True,
                    message = "Deleted successfully"
                )
            except Exception as e:
                return DeleteCart(status=False,message=e)
        elif ip:
            try:
                Cart.objects.filter(id=cart_id, ip=ip).delete()

                return DeleteCart(
                    status = True,
                    message = "Deleted successfully"
                )
            except Exception as e:
                return DeleteCart(status=False,message=e)
        else:
            return DeleteCart(status=False,message="Invalid user")
# =====================================================================================================================


class DecreaseCartItemQuantity(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    cart_item = graphene.Field(CartItemType)

    class Arguments:
        cart_id = graphene.String(required=True)
        token = graphene.String()
        ip = graphene.String()
        item_id = graphene.String(required=True)

    def mutate(self, info, cart_id, item_id, token=None, ip=None):
        if token:
            auth = authenticate_user(token)
            if not auth["status"]:
                return DecreaseCartItemQuantity(
                    status=auth["status"], message=auth["message"]
                )
            user = auth["user"]
            try:
                cart = Cart.objects.get(id=cart_id, user=user)
                if CartItem.objects.filter(id=item_id, cart=cart).exists():
                    cart_item = CartItem.objects.get(id=item_id, cart=cart)
                    quantity = cart_item.quantity - 1
                    if quantity < 1:
                        CartItem.objects.filter(id=item_id).delete()
                        return DecreaseCartItemQuantity(
                            status=True,
                            message="Item removed from cart",
                            cart_item=None,
                        )
                    else:
                        CartItem.objects.filter(id=item_id).update(quantity=quantity)
                        new_cart = CartItem.objects.get(id=item_id, cart=cart)
                        return DecreaseCartItemQuantity(
                            status=True,
                            message="Quantity reduced successfully",
                            cart_item=new_cart,
                        )
                else:
                    return DecreaseCartItemQuantity(
                        status=False, message="Cart Item does not exist"
                    )
            except Exception as e:
                return DecreaseCartItemQuantity(status=False, message=str(e))
        elif ip:
            try:
                cart = Cart.objects.get(id=cart_id, ip=ip)
                if CartItem.objects.filter(id=item_id, cart=cart).exists():
                    cart_item = CartItem.objects.get(id=item_id, cart=cart)
                    quantity = cart_item.quantity - 1
                    if quantity < 1:
                        CartItem.objects.filter(id=item_id).delete()
                        return DecreaseCartItemQuantity(
                            status=True,
                            message="Item removed from cart",
                            cart_item=None,
                        )
                    else:
                        CartItem.objects.filter(id=item_id).update(quantity=quantity)
                        new_cart = CartItem.objects.get(id=item_id, cart=cart)
                        return DecreaseCartItemQuantity(
                            status=True,
                            message="Quantity reduced successfully",
                            cart_item=new_cart,
                        )
                else:
                    return DecreaseCartItemQuantity(
                        status=False, message="Cart Item does not exist"
                    )
            except Exception as e:
                return DecreaseCartItemQuantity(status=False, message=str(e))
        else:
            return DecreaseCartItemQuantity(status=False, message="Invalid user")


class RemoveItemFromCartWithOptionId(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String()
        ip = graphene.String()
        product_option_id = graphene.String(required=True)
        quantity = graphene.Int()

    def mutate(self, info, product_option_id, quantity, token=None, ip=None):
        cart = None
        cart_item = None

        if token:
            auth = authenticate_user(token)
            if not auth["status"]:
                return RemoveItemFromCartWithOptionId(
                    status=auth["status"], message=auth["message"]
                )
            user = auth["user"]
            try:
                cart = Cart.objects.get(user=user)
            except Cart.DoesNotExist:
                return RemoveItemFromCartWithOptionId(
                    status=False, message="Cart not found"
                )
            try:
                cart_item = CartItem.objects.get(
                    cart=cart, product_option_id=product_option_id
                )
            except CartItem.DoesNotExist:
                return RemoveItemFromCartWithOptionId(
                    status=False, message="Cart item not found"
                )
        elif ip:
            try:
                cart = Cart.objects.get(ip=ip)
            except Cart.DoesNotExist:
                return RemoveItemFromCartWithOptionId(
                    status=False, message="Cart not found"
                )
            try:
                cart_item = CartItem.objects.get(
                    cart=cart, product_option_id=product_option_id
                )
            except CartItem.DoesNotExist:
                return RemoveItemFromCartWithOptionId(
                    status=False, message="Cart item not found"
                )
        else:
            return RemoveItemFromCartWithOptionId(
                status=False, message="Provide IP or token"
            )

        try:
            quantity = cart_item.quantity - 1
            if quantity < 1:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()

            return RemoveItemFromCartWithOptionId(
                status=True, message="Item removed successfully"
            )
        except Exception as e:
            return RemoveItemFromCartWithOptionId(status=False, message=str(e))


# =====================================================================================================================
class DeleteCartItem(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        cart_id = graphene.String(required=True)
        token = graphene.String()
        ip = graphene.String()
        item_id = graphene.String(required=True)

    def mutate(self, info, cart_id, item_id,token=None, ip=None):
        if token:
            auth = authenticate_user(token)
            if not auth["status"]:
                return DeleteCartItem(status=auth["status"],message=auth["message"])
            user = auth["user"]
            try:
                cart = Cart.objects.get(id=cart_id, user=user)
                cart_item = CartItem.objects.get(id=item_id)
                if cart_item:
                    CartItem.objects.filter(id=item_id, cart=cart).delete()
                return DeleteCart(
                    status = True,
                    message = "Deleted successfully"
                )
            except Exception as e:
                return DeleteCartItem(status=False,message=e)
        elif ip:
            try:
                Cart.objects.filter(id=cart_id, ip=ip).delete()

                return DeleteCartItem(
                    status = True,
                    message = "Deleted successfully"
                )
            except Exception as e:
                return DeleteCartItem(status=False,message=e)
        else:
            return DeleteCartItem(status=False,message="Invalid user")

# =====================================================================================================================

# Cart Migrate Function

def verify_cart(ip, token):
    email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
    user = ExtendUser.objects.get(email=email)
    if Cart.objects.filter(ip=ip).exists():
        cart = Cart.objects.get(ip=ip)
        cartItems = CartItem.objects.filter(cart=cart)
        if Cart.objects.filter(user=user).exists():
            userCart = Cart.objects.get(user=user)
            cartItems.update(cart=userCart)
            cart.delete()
        else:
            cart.update(user=user.id)
        Cart.objects.filter(ip=ip, user=None).delete()
    
    if not Cart.objects.filter(user=user).exists():
        Cart.objects.create(user=user)
# =====================================================================================================================


class PromoteProduct(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    product = graphene.Field(ProductType)

    class Arguments:
        token = graphene.String(required=True)
        product_id = graphene.String(required=True)
        amount = graphene.Float()
        days = graphene.Int(required=True)
    
    @staticmethod
    def mutate(self, info, token, product_id, days,amount=0.00):

        auth = authenticate_user(token)
        if not auth["status"]:
            return PromoteProduct(status=auth["status"],message=auth["message"])
        req_user = auth["user"]
        if Product.objects.filter(id=product_id).exists():
            product = Product.objects.get(id=product_id)
            if product.user == req_user or req_user.is_admin:
                if not Wallet.objects.filter(owner = product.user).exists():
                        Wallet.objects.create(
                            owner = product.user
                        )
                seller_wallet = Wallet.objects.get(owner=product.user)
                
                if not req_user.is_admin:
                    if seller_wallet.balance < amount:
                        return PromoteProduct(
                                status=False,
                                message="Insufficient balance",
                                product=product
                            )
                if product.promoted:
                    try:
                        # new_end_date = product.promo.end_date + timezone.timedelta(days=days)
                        # new_amount = product.promo.amount + amount
                        # new_balance = product.promo.balance + amount
                        ProductPromotion.objects.filter(product=product, active=True).update(end_date=F("end_date")+ timezone.timedelta(days=days), amount=F("amount")+ amount, balance=F("balance")+ amount, days=F("days")+ days)
                        if not req_user.is_admin:
                            balance = seller_wallet.balance
                            seller_wallet.balance = balance - amount
                            seller_wallet.save()
                        return PromoteProduct(
                            status=True,
                            message="Promotion extended",
                            product=product
                        )
                    except Exception as e:
                        return PromoteProduct(status=False,message=e)
                else:
                    try:
                        ProductPromotion.objects.create(
                            product=product,
                            days=days,
                            amount=amount,
                            balance=amount,
                            is_admin= True if req_user.is_admin else False,
                            start_date = timezone.now(),
                            end_date = timezone.now() + timezone.timedelta(days=days),
                        )
                        product.promoted = True
                        product.save()
                        if not req_user.is_admin:
                            balance = seller_wallet.balance
                            seller_wallet.balance = balance - amount
                            seller_wallet.save()
                        return PromoteProduct(
                            status=True,
                            message="Product promoted",
                            product=product
                        )
                    except Exception as e:
                        return PromoteProduct(status=False,message=e)
            else:
                return PromoteProduct(status=False,message="Product does not belong to you")
        else:
            return PromoteProduct(status=False,message="Product does not exist")

class CancelProductPromotion(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    promotion = graphene.Field(ProductPromotionType)

    class Arguments:
        token = graphene.String(required=True)
        product_id = graphene.String(required=True)
        
    
    @staticmethod
    def mutate(self, info, token, product_id):
        auth = authenticate_user(token)
        if not auth["status"]:
            return PromoteProduct(status=auth["status"],message=auth["message"])
        req_user = auth["user"]
        product = Product.objects.get(id=product_id)
        seller_wallet = Wallet.objects.get(owner=ExtendUser.objects.get(id=product.user.id))
        if product.user == req_user or req_user.is_admin:
            promotions = ProductPromotion.objects.filter(product=product, active=True)
            wallet_balance = seller_wallet.balance
            for promotion in promotions:
                if not promotion.is_admin:
                    wallet_balance += promotion.balance
                promotion.balance = 0
                promotion.active = False
                promotion.save()
            seller_wallet.balance = wallet_balance
            seller_wallet.save()
            product.promoted=False
            product.save()
            return CancelProductPromotion(
                            status=True,
                            message="Protion Cancelled",
                            promotion=promotion
                        )
        else:
            return CancelProductPromotion(status=False,message="Product does not belong to you")

class FlashSalesMutation(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    flash_sales = graphene.Field(FlashSalesType)

    class Arguments:
        token = graphene.String(required=True)
        productOption_id = graphene.String(required=True)
        days = graphene.Int(required=True)
        discount_percent = graphene.Float(required=True) 
        
    
    @staticmethod
    def mutate(self, info, token, productOption_id, discount_percent, days=1):
        auth = authenticate_user(token)
        if not auth["status"]:
            return FlashSalesMutation(status=auth["status"],message=auth["message"])
        user = auth["user"]
        try:
            discounted_product = ProductOption.objects.get(id=productOption_id)
            if discounted_product:
                if discounted_product.product.user == user or user.is_admin:
                    if not FlashSales.objects.filter(product=discounted_product, status=True).exists():
                            new_flash_sales = FlashSales.objects.create(
                                product=discounted_product,
                                number_of_days=days,
                                discount_percent = discount_percent,
                                status=True
                            )
                            return FlashSalesMutation(status=True,message="Flash Sale created successfully", flash_sales = new_flash_sales ) 
                    return FlashSalesMutation(status=True,message="Flash Sale already created") 
                return FlashSalesMutation(status=False,message="Product does not belong to you") 
        except Exception as e:
            return FlashSalesMutation(status=False,message=e) 


class CreateProductCharges(graphene.Mutation):
    product_charge = graphene.Field(ProductChargeType)
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String(required=True)
        has_fixed_amount = graphene.Boolean()
        charge = graphene.Float(required=True)

    @staticmethod
    def mutate(self, info, token, has_fixed_amount, charge):
        auth = authenticate_admin(token)

        if not auth["status"]:
            return CreateProductCharges(status=auth["status"], message=auth["message"])

        try:
            has_charge = ProductCharge.objects.exists()

            if has_charge:
                return CreateProductCharges(status=False, message="Already created a charge, you can only update!!!")

            product_charge = ProductCharge.objects.create(
                has_fixed_amount=has_fixed_amount,
                charge=charge
            )

            return CreateProductCharges(status=True, message="Successfully created product charges", product_charge=product_charge)

        except Exception as e:
            return CreateProductCharges(status=False, message=str(e))

class UpdateProductCharges(graphene.Mutation):
    product_charge = graphene.Field(ProductChargeType)
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String(required=True)
        id = graphene.String(required=True)
        has_fixed_amount = graphene.Boolean()
        charge = graphene.Float(required=True)

    @staticmethod
    def mutate(self, info, token, charge, id,  has_fixed_amount=False):
        auth = authenticate_admin(token)
        if not auth["status"]:
            return CreateProductCharges(status=auth["status"],message=auth["message"])
        try: 
            charges = ProductCharge.objects.get(id=id)
            if charges:
                charges.charge = charge
                charges.has_fixed_amount = has_fixed_amount
                charges.save()
                return CreateProductCharges(status=True,message="successfully updated!", product_charge=charges)
    
            return CreateProductCharges(status=False,message="Cannot find charge..Please create before updating")
        except Exception as e:
            return CreateProductCharges(status=False,message=e) 

class CreateStateDeliveryCharge(graphene.Mutation):
    delivery_charge = graphene.Field(StateDeliveryType)
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String(required=True)
        state = graphene.String(required=True)
        city = graphene.String(required=True)
        fee = graphene.Float(required=True)

    @staticmethod
    def mutate(self, info, token, state=None, fee=None, city=None):
        auth = authenticate_admin(token)
        if not auth["status"]:
            return UpdateStateDeliveryCharge(status=auth["status"],message=auth["message"])
        update_state_delivery_fees()

        if state not in nigerian_states:
                return UpdateStateDeliveryCharge(status=False,message="Cannot find state..Please check that you entered the correct state!!")
        
        if StateDeliveryFee.objects.filter(state__iexact=state, city__iexact=city).exists():
            return UpdateStateDeliveryCharge(status=False,message="city already exists for state")
        
        try:   
            state_fee = StateDeliveryFee.objects.create(
                    state=state,
                    city=city,
                    fee=fee,
                )
            return UpdateStateDeliveryCharge(status=True,message="successfully created!", delivery_charge=state_fee)
        
        except Exception as e:
            return UpdateStateDeliveryCharge(status=False,message=e) 

class UpdateStateDeliveryCharge(graphene.Mutation):
    delivery_charge = graphene.Field(StateDeliveryType)
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String(required=True)
        id = graphene.String(required=True)
        state = graphene.String()
        city = graphene.String()
        fee = graphene.Float()

    @staticmethod
    def mutate(self, info, token,id, state=None, fee=None, city=None):
        auth = authenticate_admin(token)
        if not auth["status"]:
            return UpdateStateDeliveryCharge(status=auth["status"],message=auth["message"])
        update_state_delivery_fees()
        if state:
            if state not in nigerian_states:
                    return UpdateStateDeliveryCharge(status=False,message="Cannot find state..Please check that you entered the correct state!!")
        try:   
            state_fee = StateDeliveryFee.objects.get(id=id)
            if fee:
                state_fee.fee = fee

            if state:
                state_fee.state = state

            if city:
                state_fee.city = city

            state_fee.save()
            return UpdateStateDeliveryCharge(status=True,message="successfully updated!", delivery_charge=state_fee)
        
        except Exception as e:
            return UpdateStateDeliveryCharge(status=False,message=e) 

class DeleteDeliveryCharge(graphene.Mutation):
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String(required=True)
        id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, token,id):
        auth = authenticate_admin(token)
        if not auth["status"]:
            return DeleteDeliveryCharge(status=auth["status"],message=auth["message"])
        try:   
            state_fee = StateDeliveryFee.objects.get(id=id)
            if not state_fee:
                return DeleteDeliveryCharge(status=False,message="state delivery doesn't exist")

            

            state_fee.delete()
            return DeleteDeliveryCharge(status=True,message="successfully deleted!")
        
        except Exception as e:
            return DeleteDeliveryCharge(status=False,message=e) 
