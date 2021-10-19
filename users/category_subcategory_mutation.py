import graphene
from market.models import Category, Subcategory
from graphene import String
from .data import return_category_data

data = return_category_data()


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
        return GetCategorysSubcategory(
            status=True, message="Message", category_data=cat_list
        )


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
        return GetCategorysSubcategory(
            status=True, message="Message", category_data=cat_list
        )


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
                c_category, count = Category.objects.get(name=main_category), -1
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

        def add_categories(category_list, main_category, Category, Subcategory):
            if Category.objects.filter(name=main_category).exists():
                res = add_sub_category(category_list, Category, Subcategory)
                return res
            else:
                m_ct = Category(name=main_category)
                m_ct.save()
                res = add_sub_category(category_list, Category, Subcategory)
                return res

        res = add_categories(category_list, main_category, Category, Subcategory)
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
                c_category, count = Category.objects.get(name=main_category), -1
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

        def add_categories(category_list, main_category, Category, Subcategory):
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
        return AddMultipleProductCategory(status=res["status"], message=res["message"])

        # return AddProductCategory(status=True, message=category_list, m_category=main_category)
