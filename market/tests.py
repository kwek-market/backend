# from django.db import IntegrityError
# from market.models import Category, Subcategory
# from market.vendor_array import data

# for i in data:
#     category = i[0].strip()
#     subcategory = i[1:]
#     db_category, created = Category.objects.get_or_create(name=category)
#     category_id = db_category.pk
#     subcategory_lambda = lambda x: Subcategory.objects.get_or_create(name=x.strip())
#     db_subcategory_ids = [subcategory_lambda(x) for x in subcategory]
#     for x, z in enumerate(db_subcategory_ids):
#         parent = [m[0].pk for m in db_subcategory_ids[:x]]
#         child = list(
#             set(z[0].child).union(set([m[0].pk for m in db_subcategory_ids[x + 1 :]]))
#         )
#         print("PARENT:", parent, z[0].name, end="\n")
#         z[0].categories.add(category_id)
#         z[0].parent = parent
#         z[0].child = child
#         print("CHILD:", z[0].name, z[0].child)
#         z[0].save()
