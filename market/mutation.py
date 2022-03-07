import graphene
import jwt
from django.utils import timezone
from users.validate import authenticate_user

from django.conf import settings
from market.pusher import push_to_client
from notifications.models import Message, Notification
from users.models import ExtendUser
from .models import *
from .object_types import *
from .pusher import *
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone
from wallet.models import Wallet
from django.db.models import (
    F,
    Count,
    Subquery,
    OuterRef,
    FloatField,
    IntegerField,
    BooleanField,
    TextField,
    ExpressionWrapper,
    Prefetch,
)


from .post_offices import post_offices
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
        parent = graphene.String()
    @staticmethod
    def mutate(self, info, name, parent=None):
        if Category.objects.filter(name=name).exists() and parent is None:
            return AddCategory(status=False,message="Category already exists")
        else:
            try:
                if parent is None:
                    category = Category.objects.create(name=name)
                    return AddCategory(
                        category=category,
                        status=True,
                        message="Category added successfully"
                    )
                else:
                    if Category.objects.filter(name=parent).exists():
                        parent = Category.objects.get(name=parent)
                        category = Category.objects.create(name=name, parent=parent)
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
        id = graphene.Int(required=True)
        name = graphene.String(required=True)
        parent = graphene.String()

    @staticmethod
    def mutate(self, info, name=None, parent=None, id=None):
        try:
            if Category.objects.filter(id=id).exists():
                if name is not None:
                    category = Category.objects.filter(id=id).update(name)
                    return UpdateCategory(category=category, status=True, message="Name updated successfully")
                elif parent is not None:
                    category = Category.objects.filter(id=id).update(parent)
                    return UpdateCategory(category=category, status=True, message="Parent updated successfully")
                else:
                    return UpdateCategory(status=False,message="Invalid name or parent")
            else:
                return UpdateCategory(status=False,message="Invalid id")
        except Exception as e:
            return UpdateCategory(status=False,message=e)
            

class DeleteCategory(graphene.Mutation):
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        id = graphene.Int(required=True)

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
        p_cat = Category.objects.get(id=category)
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
            quantity = "" if "quantity" not in keys else option["quantity"]
            price = "" if "price" not in keys else option["price"]
            discounted_price = "" if "discounted_price" not in keys else option["discounted_price"]
            option_total_price = 0.0
            ProductOption.objects.create(product=product, size=size, quantity=quantity, price=price, discounted_price=discounted_price, option_total_price=option_total_price)
        
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
                ProductPromotion.objects.filter(product=product).update(link_clicks=F('link_clicks')+1)
                # link_clicks = product.promo.link_clicks + 1
                # promo = ProductPromotion.objects.get(product=product)
                # promo.link_clicks = link_clicks
                # promo.save()
            clicks = product.clicks + 1
            product.clicks = clicks
            product.save()
            return ProductClick(
                status = True,
                message = "Click added"
            )
        else:
            return ProductClick(status=False,message="Invalid Product")
class UpdateProductMutation(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        id = graphene.Int(required=True)
        product_data = ProductInput(required=True)
        

    @staticmethod
    def mutate(root, info, id=None, product_data=None):
        product = Product.objects.filter(id=id)
        product.update(**product_data)
        return CreateProduct(product=product.first())
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

    @staticmethod
    def mutate(self, info, product_option_id, token=None, ip_address=None):
        option = ProductOption.objects.get(id=product_option_id)
        product = Product.objects.get(options__id=product_option_id)
        if token:
            auth = authenticate_user(token)
            if not auth["status"]:
                return CreateCartItem(status=auth["status"],message=auth["message"])
            user = auth["user"]
            if user:
                try:
                    user_cart = user.user_carts
                except Exception:
                    user_cart = Cart.objects.create(user=user)
                
                has_product = Cart.objects.filter(user=user, cart_item__product=product, cart_item__product__options=option, cart_item__ordered=False)

                if has_product:
                    cart_item = CartItem.objects.get(cart__user=user, product=product, product__options=option, ordered=False)
                    initial_price = cart_item.price/cart_item.quantity
                    quantity = int(cart_item.quantity) + 1
                    price = int(cart_item.price) + initial_price
                    cart_item = CartItem.objects.filter(id=cart_item.id, product=cart_item.product).update(quantity=quantity, price=price)
                    return CreateCartItem(
                        cart_item=cart_item,
                        status = True,
                        message = "Added to cart"
                    )
                else:
                    try:
                        if option.discounted_price:
                            cart_item = CartItem.objects.create(product=product, quantity=1, price=option.discounted_price, cart=user_cart, product_option_id=product_option_id)
                        else:
                            cart_item = CartItem.objects.create(product=product, quantity=1, price=option.price, cart=user_cart, product_option_id=product_option_id)
                        return CreateCartItem(
                            cart_item=cart_item,
                            status = True,
                            message = "Added to cart"
                        )
                    except Exception as e:
                        return CreateCartItem(status=False,message=e)
        elif ip_address:
            try:
                user_cart = Cart.objects.get(ip=ip_address)
            except Exception:
                user_cart = Cart.objects.create(ip=ip_address)

            has_product = Cart.objects.filter(ip=ip_address, cart_item__product=product, cart_item__product__options=option, cart_item__ordered=False)

            if has_product:
                cart_item = CartItem.objects.get(cart__ip=ip_address, product=product, product__options=option)
                initial_price = cart_item.price/cart_item.quantity
                quantity = int(cart_item.quantity) + 1
                price = int(cart_item.price) + initial_price
                cart_item = CartItem.objects.filter(id=cart_item.id, product=cart_item.product).update(quantity=quantity, price=price)
                return CreateCartItem(
                    cart_item=cart_item,
                    status = True,
                    message = "Added to cart"
                )
            else:
                try:
                    if option.discounted_price:
                        cart_item = CartItem.objects.create(product=product, quantity=1, price=option.discounted_price, cart=user_cart, product_option_id=product_option_id)
                    else:
                        cart_item = CartItem.objects.create(product=product, quantity=1, price=option.price, cart=user_cart, product_option_id=product_option_id)
                    return CreateCartItem(
                        cart_item=cart_item,
                        status = True,
                        message = "Added to cart"
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

    def mutate(self, info, cart_id, item_id,token=None, ip=None):
        if token:
            auth = authenticate_user(token)
            if not auth["status"]:
                return DecreaseCartItemQuantity(status=auth["status"],message=auth["message"])
            user = auth["user"]
            try:
                cart = Cart.objects.get(id=cart_id, user=user)
                if CartItem.objects.filter(id=item_id, cart=cart).exists():
                    cart_item = CartItem.objects.get(id=item_id, cart=cart)
                    quantity = cart_item.quantity-1
                    initial_price = cart_item.price/cart_item.quantity
                    price = cart_item.price - initial_price
                    if quantity < 1:
                        print("quantity", quantity)
                        CartItem.objects.filter(id=item_id).delete()
                    else:
                        print("price",  price)
                        CartItem.objects.filter(id=item_id).update(quantity=quantity, price=price)
                    new_cart = CartItem.objects.get(id=item_id, cart=cart)
                    return DecreaseCartItemQuantity(
                        status = True,
                        message = "Quantity reduced successfully",
                        cart_item = new_cart
                    )
                else:
                    return DecreaseCartItemQuantity(status=False,message="Cart Item does not exist")
            except Exception as e:
                return DecreaseCartItemQuantity(status=False,message=e)
        elif ip:
            try:
                cart = Cart.objects.get(id=cart_id, ip=ip)
                if CartItem.objects.filter(id=item_id, cart=cart).exists():
                    cart_item = CartItem.objects.get(id=item_id, cart=cart)
                    quantity = cart_item.quantity-1
                    if quantity < 1:
                        CartItem.objects.filter(id=item_id).delete()
                    else:
                        CartItem.objects.filter(id=item_id).update(quantity=quantity)
                return DeleteCart(
                    status = True,
                    message = "Quantity reduced successfully"
                )
            except Exception as e:
                return DecreaseCartItemQuantity(status=False,message=e)
        else:
            return DecreaseCartItemQuantity(status=False,message="Invalid user")
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
    cart = Cart.objects.filter(ip=ip)
    email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
    user = ExtendUser.objects.get(email=email)
    if cart:
        for item in cart:
            product = item.product
            quantity = item.quantity
            price = item.price
            Cart.objects.create(user_id=user, product=product, quantity=quantity, price=price)
        Cart.objects.filter(id=cart.id, ip=ip).delete()
    pass
# =====================================================================================================================


class PromoteProduct(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    product = graphene.Field(ProductType)

    class Arguments:
        token = graphene.String(required=True)
        product_id = graphene.String(required=True)
        amount = graphene.Float(required=True)
        days = graphene.Int(required=True)
    
    @staticmethod
    def mutate(self, info, token, product_id, amount, days):

        auth = authenticate_user(token)
        if not auth["status"]:
            return PromoteProduct(status=auth["status"],message=auth["message"])
        user = auth["user"]
        if Product.objects.filter(id=product_id).exists():
            product = Product.objects.get(id=product_id)
            if product.user == user:
                seller_wallet = Wallet.objects.get(owner=user)
                if seller_wallet.balance < amount:
                    return PromoteProduct(
                            status=False,
                            message="Insufficient balance",
                            product=product
                        )
                if product.promoted:
                    try:
                        from datetime import timedelta
                        new_end_date = product.promo.end_date + timedelta(days=days)
                        ProductPromotion.objects.filter(product=product).update(end_date=new_end_date)
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
                            start_date = timezone.now()
                        )
                        product.promoted = True
                        product.save()
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



def unpromote():
    from datetime import timedelta, datetime
    # now = datetime.now()
    now = timezone.now()
    all_products = Product.objects.filter(promoted=True, promo__end_date__lte = now)
    for product in all_products:
            # if (product.promo.start_date + now) > product.promo.end_date:
                Product.objects.filter(id=product.id).update(promoted=False)
                ProductPromotion.objects.filter(product=product).update(active=False)
    
    
# trigger = CronTrigger(
#     year="*", month="*", day="*", hour="8", minute="0", second="0"
# )
sched.add_job(unpromote, 'interval', minutes=20)
sched.start()



