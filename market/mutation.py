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
    keyword = graphene.List(graphene.Int)
    clicks = graphene.Int()
    promoted = graphene.Boolean()

class AddCategory(graphene.Mutation):
    category = graphene.String()
    subcategory = graphene.String()
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
                        category=category.name,
                        status=True,
                        message="Category added successfully"
                    )
                else:
                    if Category.objects.filter(name=parent).exists():
                        parent = Category.objects.get(name=parent)
                        category = Category.objects.create(name=name, parent=parent)
                        return AddCategory(
                            category=parent.name,
                            subcategory=category.name,
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
    category = graphene.String()
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

class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String(required=True)
        product_title = graphene.String(required=True)
        category = graphene.String(required=True)
        brand = graphene.String()
        product_weight = graphene.String()
        short_description = graphene.String()
        charge_five_percent_vat = graphene.Boolean(required=True)
        return_policy = graphene.String()
        warranty = graphene.String()
        color = graphene.String()
        gender = graphene.String()
        keyword = graphene.Int()
        clicks = graphene.Int()
        promoted = graphene.Boolean()

    @staticmethod
    def mutate(
        self,
        info,
        token, 
        product_title,
        category,
        charge_five_percent_vat,
        keyword,
        brand=None,
        product_weight=None,
        short_description=None,
        return_policy=None,
        warranty=None,
        color=None,
        gender=None,
        clicks=None,
        promoted=None
    ):
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
        user = ExtendUser.objects.get(email=email)
        p_cat = Category.objects.get(name=category)
        
        if Keyword.objects.filter(id=keyword).exists():
            p_keyword = Keyword.objects.get(keyword=keyword)
        else:
            Keyword.objects.create(keyword=product_title)
            p_keyword = Keyword.objects.get(keyword=keyword)
            print(p_keyword)

        product = Product.objects.create(
            keyword.set(p_keyword),
            product_title=product_title,
            user=user,
            category=p_cat,
            brand=brand,
            product_weight=product_weight,
            short_description=short_description,
            charge_five_percent_vat=charge_five_percent_vat,
            return_policy=return_policy,
            warranty=warranty,
            color=color,
            gender=gender,
            clicks=clicks,
            promoted=promoted
        )
        return CreateProduct(
            product=product,
            status=True,
            message="Product added"
        )


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

class WishListMutation(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String()
        product_id = graphene.String()
        is_check = graphene.Boolean()

    @staticmethod
    def mutate(self, info, product_id, token, is_check=False):
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
        user = ExtendUser.objects.get(email=email)
        
        if user.exists():
            try:
                try:
                    product = Product.objects.get(id=product_id)
                except Exception:
                    raise Exception("Product with product_id does not exist")

                try:
                    user_wish = info.context.user.user_wish
                except Exception:
                    user_wish = Wishlist.objects.create(user_id=info.context.user.id)

                has_product = user_wish.products.filter(id=product_id)

                if has_product:
                    if is_check:
                        return WishListMutation(status=True)
                    user_wish.products.remove(product)
                else:
                    if is_check:
                        return WishListMutation(status=False)
                    user_wish.products.add(product)

                return WishListMutation(
                    status = True,
                    message = "Successful"
                )
            except Exception as e:
                return {
                    "status": False,
                    "message": e
                }

class CreateCartItem(graphene.Mutation):
    cart_item = graphene.Field(CartType)
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String(required=False)
        ip_address = graphene.String(required=False)
        product_id = graphene.String(required=True)
        quantity = graphene.String(required=False)

    @staticmethod
    def mutate(self, info, token, product_id, quantity, ip_address):
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["username"]
        user = ExtendUser.objects.get(email=email)
        product = Product.objects.get(id=product_id)
        price = product.price
        if user.exists():
            try:
                cart_item = Cart.objects.create(product=product, user=user, quantity=quantity, price=price)
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
                cart_item = Cart.objects.create(product=product, id=ip_address, quantity=quantity, price=price)
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


class UpdateCartItem(graphene.Mutation):
    cart_item = graphene.Field(CartType)

    class Arguments:
        cart_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)

    @staticmethod
    def mutate(self, info, cart_id, quantity):
        try:
            Cart.objects.filter(id=cart_id, user_id=info.context.user.id).update(quantity)

            return UpdateCartItem(
                cart_item = Cart.objects.get(id=cart_id),
                status = True,
                message = "Cart Updated"
            )
        except Exception as e:
            return {
                "status": False,
                "message": e
            }
class DeleteCartItem(graphene.Mutation):
    status = graphene.Boolean()

    class Arguments:
        cart_id = graphene.ID(required=True)

    def mutate(self, info, cart_id):
        try:
            Cart.objects.filter(id=cart_id, user_id=info.context.user.id).delete()

            return DeleteCartItem(
                status = True,
                message = "Deleted successfully"
            )
        except Exception as e:
            return {
                "status": False,
                "message": e
            }

def verify_cart(ip, token):
    cart = Query.carts(token={}, ip=ip)
    if cart:
        for item in cart:
            token = token
            product_id = item.product_id
            quantity = item.quantity
            CreateCartItem(token, product_id, quantity)
    pass