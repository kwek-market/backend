import graphene
from graphql import GraphQLError
import jwt

from django.conf import settings
from users.models import ExtendUser
from .models import *
from .object_types import *
from graphene import List, String
from users.data import return_category_data
from users.queries import Query


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
            return {
                "status": False,
                "message": "Category already exists"
            }
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
                        return {
                            "status": False,
                            "message": "Parent category does not exist"
                        }
            except Exception as e:
                return {
                    "status": False,
                    "message": e
                }

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
                    return{
                        "status": False,
                        "message": "Invalid name or parent"
                    }
            else:
                return {
                    "status": False,
                    "message": "Invalid id"
                }
        except Exception as e:
            return {
                "status": False,
                "message": e
            }
            

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
                return {
                    "status": False,
                    "message": "Invalid id"
                }
        except Exception as e:
            return {
                "status": False,
                "message": e
            }
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
        product_weight = graphene.String()
        product_image_url = graphene.List(graphene.String, required=True)
        short_description = graphene.String()
        charge_five_percent_vat = graphene.Boolean(required=True)
        return_policy = graphene.String()
        warranty = graphene.String()
        # product_options = graphene.List(graphene.String)
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
        brand="",
        product_weight="",
        short_description="",
        return_policy="",
        warranty="",
        color="",
        gender=""
    ):
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
        user = ExtendUser.objects.get(email=email)
        p_cat = Category.objects.get(name=category)
        sub_cat = Category.objects.get(name=subcategory)
        

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
        return CreateProduct(
            product=product,
            status=True,
            message="Product added"
        )


class ProductClick(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String(required=True)
        product_id = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, token, product_id):
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
        user = ExtendUser.objects.filter(email=email)
        product = Product.objects.get(id=product_id)
        if user.exists():
            if product:
                clicks = product.clicks + 1
                Product.objects.filter(id=product.id).update(clicks=clicks)
                return ProductClick(
                    status = True,
                    message = "Click added"
                )
            else:
                return {
                    "status": False,
                    "message": "Invalid Product"
                }
        else:
            return {
                "status": False,
                "message": "Invalid User"
            }
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
        comment = graphene.String()
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
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
        user = ExtendUser.objects.get(email=email)
        
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
                    return {
                        "status": False,
                        "message": "Invalid Vote"
                    }
            
        
        if user:
            if product and (review is not None) and (rating is not None):
                product_review=Rating.objects.create(
                    user=user,
                    product=product,
                    rating=rating,
                    review=review
                )
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
                return Reviews(
                    product_review=product_review,
                    status=True,
                    message="Rating added successfully"
                )
            else:
                return {
                    "status": False,
                    "message": "Invaid Product"
                }
        else:
            return {
                "status": False,
                "message": "Invalid user"
            }
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


# Wishlist Mutation
class WishListMutation(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String()
        product_id = graphene.String()

    @staticmethod
    def mutate(self, info, product_id, token, is_check=False):
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
        user = ExtendUser.objects.get(email=email)
        
        if user:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return {
                    "status" : False,
                    "message" : "Product with product_id does not exist"
                }

            try:
                user_wish = user.user_wish
            except Exception:
                user_wish = Wishlist.objects.create(user_id=user.id)

            has_product = user_wish.products.filter(id=product_id)

            if has_product:
                user_wish.products.remove(product)
            else:
                user_wish.products.add(product)
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
        product_id = graphene.String(required=True)
        quantity = graphene.Int()
        price = graphene.String()

    @staticmethod
    def mutate(self, info, product_id, price, quantity, token=None, ip_address=None):
        product = Product.objects.get(id=product_id)
        price = price
        if token:
            email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
            user = ExtendUser.objects.get(email=email)
            if user:
                try:
                    user_cart = user.user_carts
                except Exception:
                    user_cart = Cart.objects.create(user=user)
                
                has_product = Cart.objects.filter(user=user, cart_item__product=product)

                if has_product:
                    cart_item = CartItem.objects.get(product=product)
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
                        cart_item = CartItem.objects.create(product=product, quantity=quantity, price=price, cart=user_cart)
                        return CreateCartItem(
                            cart_item=cart_item,
                            status = True,
                            message = "Added to cart"
                        )
                    except Exception as e:
                        return {
                            "status": False,
                            "message": e
                        }
        elif ip_address:
            try:
                user_cart = Cart.objects.filter(ip=ip_address)
            except Exception:
                user_cart = Cart.objects.create(ip=ip_address)
            
            has_product = user_cart.product.filter(id=product_id)

            if has_product:
                quantity = int(has_product.quantity) + 1
                Cart.objects.filter(id=user_cart.id, ip=ip_address).update(quantity=quantity)
            try:
                cart_item = Cart.objects.create(product=product, ip=ip_address, quantity=quantity, price=price)
                return CreateCartItem(
                    cart_item=cart_item,
                    status = True,
                    message = "Added to cart"
                )
            except Exception as e:
                return {
                    "status": False,
                    "message": e
                }
        else:
            return {
                "status": False,
                "message": "Invalid user"
            }

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
            email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
            user = ExtendUser.objects.get(email=email)
            try:
                Cart.objects.filter(id=cart_id, user_id=user).delete()

                return DeleteCart(
                    status = True,
                    message = "Deleted successfully"
                )
            except Exception as e:
                return {
                    "status": False,
                    "message": e
                }
        elif ip:
            try:
                Cart.objects.filter(id=cart_id, ip=ip).delete()

                return DeleteCart(
                    status = True,
                    message = "Deleted successfully"
                )
            except Exception as e:
                return {
                    "status": False,
                    "message": e
                }
        else:
            return {
                "status": False,
                "message": "Invalid user"
            }
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
            email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
            user = ExtendUser.objects.get(email=email)
            try:
                cart = Cart.objects.filter(id=cart_id, user_id=user)
                for item in cart:
                    if item.product.id == item_id:
                        cart.product.remove(item)

                return DeleteCart(
                    status = True,
                    message = "Deleted successfully"
                )
            except Exception as e:
                return {
                    "status": False,
                    "message": e
                }
        elif ip:
            try:
                Cart.objects.filter(id=cart_id, ip=ip).delete()

                return DeleteCart(
                    status = True,
                    message = "Deleted successfully"
                )
            except Exception as e:
                return {
                    "status": False,
                    "message": e
                }
        else:
            return {
                "status": False,
                "message": "Invalid user"
            }
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