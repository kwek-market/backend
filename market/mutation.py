import graphene
from graphql import GraphQLError

from users.models import ExtendUser
from .models import *
from .object_types import *
from graphene import List, String
from users.data import return_category_data

data = return_category_data()


class CategoryInput(graphene.InputObjectType):
    id = graphene.Int()
    name = graphene.String(required=True)


class ProductInput(graphene.InputObjectType):
    id = graphene.String()
    product_title = graphene.String(required=True)
    user_id = graphene.Int(required=True)
    subcategory_id = graphene.Int(required=True)
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

class NewsletterInput(graphene.InputObjectType):
    id = graphene.Int()
    email = graphene.String()

class CartInput(graphene.InputObjectType):
    id = graphene.Int()
    user = graphene.String()
    products = graphene.String()

class WishlistInput(graphene.InputObjectType):
    id = graphene.Int()
    user = graphene.String()
    products = graphene.String()

class UpdateCategoryMutation(graphene.Mutation):
    message = graphene.String()
    category = graphene.Field(CategoryType)
    status = graphene.Boolean()

    class Arguments:
        id = graphene.Int(required=True)
        category_data = CategoryInput(required=True)

    @staticmethod
    def mutate(root, info, id=None, category_data=None):
        category = Category.objects.get(id=id)
        category.name = category_data.name
        category.save()
        return UpdateCategoryMutation(category=category, status=True)


class CreateProductMutation(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        product_data = ProductInput(required=True)

    @staticmethod
    def mutate(root, info, product_data=None):
        product = Product.objects.create(**product_data)
        return CreateProductMutation(product=product)


class UpdateProductMutation(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        id = graphene.Int(required=True)
        product_data = ProductInput(required=True)

    @staticmethod
    def mutate(root, info, id=None, product_data=None):
        product = Product.objects.filter(id=id)
        product.update(**product_data)
        return CreateProductMutation(product=product.first())


class GetCategorysSubcategory(graphene.Mutation):
    message = graphene.String()
    status = graphene.Boolean()
    category_data = graphene.List(String)

    class Arguments:
        category = graphene.Int()

    @staticmethod
    def mutate(self, info, category):
        all_subs = list(Subcategory.objects.filter(category=category).values())
        category_name = Category.objects.get(id=category).name
        cat_list = [{category_name: []}]

        def get_last_sub_categories(all_subs):
            last_subs = []
            for i in all_subs:
                if i["child"] == False:
                    last_subs.append(i)
            return last_subs

        def get_next_sub(all_subs, st_list):
            start_list = st_list
            current = start_list[-1]
            if len(start_list) > 1:
                for i in all_subs:
                    # if i['name'] == current and i['parent'] == True and i['childcategory'] == start_list[-2]:
                    if i["name"] == current and i["parent"] == True:
                        parent = i["parentcategory"]
                        start_list.append(parent)
                        for j in all_subs:
                            # if j['name'] == parent and j['parent'] == True and j['childcategory'] == start_list[-2]:
                            if j["name"] == parent and j["parent"] == True:
                                start_list = get_next_sub(all_subs, start_list)
                return start_list

            else:
                for i in all_subs:
                    if i["name"] == current and i["parent"] == True:
                        parent = i["parentcategory"]
                        start_list.append(parent)
                        start_list = get_next_sub(all_subs, start_list)
                return start_list

        def get_subsets(all_subs):
            last_subs = get_last_sub_categories(all_subs)
            ct_list = []
            for i in last_subs:
                this_sub = []
                this_sub.append(i["name"])
                this_sub = get_next_sub(all_subs, this_sub)
                this_sub = list(reversed(this_sub))
                ct_list.append(this_sub)
            return ct_list

        subsets = get_subsets(all_subs)
        cat_list[0][category_name] = subsets

        # print(all_subs)
        return GetCategorysSubcategory(status=True,
                                       message="Message",
                                       category_data=cat_list)


class GetAllCategorysSubcategory(graphene.Mutation):
    message = graphene.String()
    status = graphene.Boolean()
    category_data = graphene.List(String)
    # class Arguments:
    #     category = graphene.Int()

    @staticmethod
    def mutate(self, info):
        # all_subs = list(Subcategory.objects.all().values())
        all_categories = list(Category.objects.all().values())
        cat_dict = {}
        cat_id_list = []
        for p in all_categories:
            c_id, c_name = p["id"], p["name"]
            cat_dict[c_id] = c_name
            cat_id_list.append(c_id)
        cat_list = [{}]

        def get_last_sub_categories(all_subs):
            last_subs = []
            for i in all_subs:
                if i["child"] == False:
                    last_subs.append(i)
            return last_subs

        def get_next_sub(all_subs, st_list):
            start_list = st_list
            current = start_list[-1]
            if len(start_list) > 1:
                for i in all_subs:
                    # if i['name'] == current and i['parent'] == True and i['childcategory'] == start_list[-2]:
                    if i["name"] == current and i["parent"] == True:
                        parent = i["parentcategory"]
                        start_list.append(parent)
                        for j in all_subs:
                            # if j['name'] == parent and j['parent'] == True and j['childcategory'] == start_list[-2]:
                            if j["name"] == parent and j["parent"] == True:
                                start_list = get_next_sub(all_subs, start_list)
                return start_list

            else:
                for i in all_subs:
                    if i["name"] == current and i["parent"] == True:
                        parent = i["parentcategory"]
                        start_list.append(parent)
                        start_list = get_next_sub(all_subs, start_list)
                return start_list

        def get_subsets(all_subs):
            last_subs = get_last_sub_categories(all_subs)
            ct_list = []
            for i in last_subs:
                this_sub = []
                this_sub.append(i["name"])
                this_sub = get_next_sub(all_subs, this_sub)
                this_sub = list(reversed(this_sub))
                ct_list.append(this_sub)
            return ct_list

        for g in cat_id_list:
            all_subs = list(Subcategory.objects.filter(category=g).values())
            subsets = get_subsets(all_subs)
            category_name = cat_dict[g]
            cat_list[0][category_name] = subsets
        # subsets = get_subsets(all_subs)
        # cat_list[0][category_name] = subsets

        # print(all_subs)
        return GetCategorysSubcategory(status=True,
                                       message="Message",
                                       category_data=cat_list)


class AddProductCategory(graphene.Mutation):
    # user = graphene.Field(UserType)
    # category = graphene.Field(CategoryType)
    # Subcategory = graphene.Field(SubcategoryType)
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        category_list = graphene.List(String)

    @staticmethod
    def mutate(self, info, category_list):
        main_category, ct_len = category_list[0], len(category_list)
        ct_lp = ct_len - 1

        def save_sub_category(
            name,
            category,
            parentcategory,
            childcategory,
            parent,
            child,
            Category,
            Subcategory,
        ):
            sub_ct = Subcategory(
                name=name,
                category=category,
                parentcategory=parentcategory,
                childcategory=childcategory,
                parent=parent,
                child=child,
            )
            sub_ct.save()

        def add_sub_category(category_list, Category, Subcategory):
            main_category, ct_len = category_list[0], len(category_list)
            ct_lp = ct_len - 1
            try:
                c_category, count = Category.objects.get(
                    name=main_category), -1
                category_id = c_category.id
                for i in category_list:
                    count += 1
                    if count != 0:
                        if count == 1:
                            if Subcategory.objects.filter(name=i).exists():
                                sub_category = Subcategory.objects.get(name=i)
                                s_category = sub_category.category.id
                                ss_category = sub_category.category
                                # if s_category != category_id:
                                if ss_category != c_category:
                                    if count == ct_lp:
                                        save_sub_category(
                                            i,
                                            c_category,
                                            "",
                                            "",
                                            False,
                                            False,
                                            Category,
                                            Subcategory,
                                        )
                                    else:
                                        save_sub_category(
                                            i,
                                            c_category,
                                            "",
                                            category_list[count + 1],
                                            False,
                                            True,
                                            Category,
                                            Subcategory,
                                        )
                            else:
                                save_sub_category(
                                    i,
                                    c_category,
                                    "",
                                    category_list[count + 1],
                                    False,
                                    True,
                                    Category,
                                    Subcategory,
                                )
                        else:
                            if Subcategory.objects.filter(name=i).exists():
                                sub_category = Subcategory.objects.get(name=i)
                                s_category = sub_category.category.id
                                ss_category = sub_category.category
                                # if s_category != category_id:
                                if ss_category != c_category:
                                    if count == ct_lp:
                                        save_sub_category(
                                            i,
                                            c_category,
                                            category_list[count - 1],
                                            "",
                                            True,
                                            False,
                                            Category,
                                            Subcategory,
                                        )
                                    else:
                                        save_sub_category(
                                            i,
                                            c_category,
                                            category_list[count - 1],
                                            category_list[count + 1],
                                            True,
                                            True,
                                            Category,
                                            Subcategory,
                                        )
                            else:
                                if count == ct_lp:
                                    save_sub_category(
                                        i,
                                        c_category,
                                        category_list[count - 1],
                                        "",
                                        True,
                                        False,
                                        Category,
                                        Subcategory,
                                    )
                                else:
                                    save_sub_category(
                                        i,
                                        c_category,
                                        category_list[count - 1],
                                        category_list[count + 1],
                                        True,
                                        True,
                                        Category,
                                        Subcategory,
                                    )
                return {"status": True, "message": "Successful"}
            except Exception as e:
                return {"status": False, "message": e}

        def add_categories(category_list, main_category, Category,
                           Subcategory):
            if Category.objects.filter(name=main_category).exists():
                res = add_sub_category(category_list, Category, Subcategory)
                return res
            else:
                m_ct = Category(name=main_category)
                m_ct.save()
                res = add_sub_category(category_list, Category, Subcategory)
                return res

        res = add_categories(category_list, main_category, Category,
                             Subcategory)
        return AddProductCategory(status=res["status"], message=res["message"])


class AddMultipleProductCategory(graphene.Mutation):
    # user = graphene.Field(UserType)
    # category = graphene.Field(CategoryType)
    # Subcategory = graphene.Field(SubcategoryType)
    message = graphene.String()
    status = graphene.Boolean()

    # class Arguments:
    #     category_list = graphene.List(String)

    @staticmethod
    def mutate(self, info):
        # main_category, ct_len = category_list[0], len(category_list)
        # ct_lp = ct_len-1
        def save_sub_category(
            name,
            category,
            parentcategory,
            childcategory,
            parent,
            child,
            Category,
            Subcategory,
        ):
            sub_ct = Subcategory(
                name=name,
                category=category,
                parentcategory=parentcategory,
                childcategory=childcategory,
                parent=parent,
                child=child,
            )
            sub_ct.save()

        def add_sub_category(category_list, Category, Subcategory):
            main_category, ct_len = category_list[0], len(category_list)
            ct_lp = ct_len - 1
            try:
                c_category, count = Category.objects.get(
                    name=main_category), -1
                category_id = c_category.id
                for i in category_list:
                    count += 1
                    if count != 0:
                        if count == 1:
                            if Subcategory.objects.filter(name=i).exists():
                                sub_category = Subcategory.objects.get(name=i)
                                s_category = sub_category.category.id
                                ss_category = sub_category.category
                                # if s_category != category_id:
                                if ss_category != c_category:
                                    if count == ct_lp:
                                        save_sub_category(
                                            i,
                                            c_category,
                                            "",
                                            "",
                                            False,
                                            False,
                                            Category,
                                            Subcategory,
                                        )
                                    else:
                                        save_sub_category(
                                            i,
                                            c_category,
                                            "",
                                            category_list[count + 1],
                                            False,
                                            True,
                                            Category,
                                            Subcategory,
                                        )
                            else:
                                save_sub_category(
                                    i,
                                    c_category,
                                    "",
                                    category_list[count + 1],
                                    False,
                                    True,
                                    Category,
                                    Subcategory,
                                )
                        else:
                            if Subcategory.objects.filter(name=i).exists():
                                sub_category = Subcategory.objects.get(name=i)
                                s_category = sub_category.category.id
                                ss_category = sub_category.category
                                # if s_category != category_id:
                                if ss_category != c_category:
                                    if count == ct_lp:
                                        save_sub_category(
                                            i,
                                            c_category,
                                            category_list[count - 1],
                                            "",
                                            True,
                                            False,
                                            Category,
                                            Subcategory,
                                        )
                                    else:
                                        save_sub_category(
                                            i,
                                            c_category,
                                            category_list[count - 1],
                                            category_list[count + 1],
                                            True,
                                            True,
                                            Category,
                                            Subcategory,
                                        )
                            else:
                                if count == ct_lp:
                                    save_sub_category(
                                        i,
                                        c_category,
                                        category_list[count - 1],
                                        "",
                                        True,
                                        False,
                                        Category,
                                        Subcategory,
                                    )
                                else:
                                    save_sub_category(
                                        i,
                                        c_category,
                                        category_list[count - 1],
                                        category_list[count + 1],
                                        True,
                                        True,
                                        Category,
                                        Subcategory,
                                    )
                return {"status": True, "message": "Successful"}
            except Exception as e:
                return {"status": False, "message": e}

        def add_categories(category_list, main_category, Category,
                           Subcategory):
            if Category.objects.filter(name=main_category).exists():
                res = add_sub_category(category_list, Category, Subcategory)
                return res
            else:
                m_ct = Category(name=main_category)
                m_ct.save()
                res = add_sub_category(category_list, Category, Subcategory)
                return res

        for d in data:
            res = add_categories(d, d[0], Category, Subcategory)
        return AddMultipleProductCategory(status=res["status"],
                                          message=res["message"])

        # return AddProductCategory(status=True, message=category_list, m_category=main_category)


class CreateSubscriberMutation(graphene.Mutation):
    subscriber = graphene.Field(NewsletterType)
    message = graphene.String()
    status = graphene.Boolean()
    class Arguments:
        email = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, email):
        if Newsletter.objects.filter(email=email).exists():
            return CreateSubscriberMutation(
                status=False, message="You have already subscribed")
        else:
            subscriber = Newsletter(email=email)
            subscriber.save()
        return CreateSubscriberMutation(subscriber=subscriber,
                                        status=True,
                                        message="Subscription Successful")

class WishListMutation(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        product_id = graphene.ID(required=True)
        is_check = graphene.Boolean()

    def mutate(self, info, product_id, is_check=False):
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
        product_id = graphene.ID(required=True)
        quantity = graphene.Int()
        price = graphene.Float()

    def mutate(self, info, product_id, **kwargs):
        try:
            Cart.objects.filter(product_id=product_id, user_id=info.context.user.id).delete()

            cart_item = Cart.objects.create(product_id=product_id, user_id=info.context.user.id, **kwargs)

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


class UpdateCartItem(graphene.Mutation):
    cart_item = graphene.Field(CartType)

    class Arguments:
        cart_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)
        price = graphene.Float(required=True)

    def mutate(self, info, cart_id, **kwargs):
        try:
            Cart.objects.filter(id=cart_id, user_id=info.context.user.id).update(**kwargs)

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