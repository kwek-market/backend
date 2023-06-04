from django.utils import timezone
from django.views import View
from django.http import JsonResponse
from asset_mgmt.models import AssetFile
from django.core.files.storage import FileSystemStorage
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseNotModified,
)
from django.contrib.auth import get_user_model
import uuid
import threading

import mimetypes
from PIL import Image
from django.utils.http import http_date, parse_http_date
from django.views.static import directory_index, was_modified_since
from django.utils._os import safe_join
from pathlib import Path
from kwek.vendor_array import data
from market.models import (
    Category,
    Product,
    ProductImage,
    ProductOption,
    Keyword,
    ProductPromotion,
    Rating,
)
from users.models import ExtendUser, SellerProfile
import posixpath
import json
import random


# Create your views here.
with open("asset_mgmt/kwek.json", "r") as file:
    products = json.load(file)

allowed_imgs = ["jpg", "png", "jpeg", "svg"]
allowed_files = ["pdf", "docx"]


class FileAssetView(View):
    def post(self, request, *args, **kwargs):
        upload = request.FILES.getlist("upload")
        resp = {}
        for i in upload:
            fss = FileSystemStorage()
            if (
                i.name.split(".")[-1].lower()
                and i.content_type.split("/")[-1].lower() not in allowed_files
            ):
                resp[i.name] = "invalid file type"
                continue
            file = fss.save(f"file/{i.name}", i)
            file_url = fss.url(file)
            resp[i.name] = file_url
        return JsonResponse(resp)


class PopulateCategory(View):
    def get(self, request):
        thread = threading.Thread(target=populate_categories)
        thread.start()
        return JsonResponse({"status": True, "message": "started populating"})

def get_icon(category_name:str) -> str:
    switch = {
        "Automotive & Industrial": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296183/car_1_eymdl8.svg",
        "Baby and Toddler Toys": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296185/toys_1_tg5gsv.svg",
        "Health, Beauty and Personal care": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296185/stones_1_jlcfsd.svg",
        "Books & Media Library": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296183/layers_1_wgfk8s.svg",
        "Computer Electronics and Accessories": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296183/electronics_1_kitsab.svg",
        "Foods, Drinks & Groceries": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296183/layers_1_wgfk8s.svg",
        "Electronics": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296183/electronics_1_kitsab.svg",
        "Protectors & Skins": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296185/stones_1_jlcfsd.svg",
        "Home and Kitchen": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296183/electronics_1_kitsab.svg",
        "Kwek Fashion and Style": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296183/dress_1_sjs5ac.svg",
        "Kwek Phones and Tablets": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296183/layers_1_wgfk8s.svg",
        "Office & School Supplies": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296183/house_1_s9j3uo.svg",
        "Sports and Fitness": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296183/sports_1_bbdtco.svg",
        "Kwek Other Searches": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296183/layers_1_wgfk8s.svg",
        "": "https://res.cloudinary.com/psami-wondah/image/upload/v1685296183/layers_1_wgfk8s.svg"
    }

    icon = switch[category_name]
    return icon if icon != "" else switch[""]

def populate_categories():
    category_count = 1
    sub_category_count = 1
    for array in data:
        print("category count", category_count)
        category_count+= 1
        icon = get_icon(array[0])
        if Category.objects.filter(name=array[0]).exists():
            cate = Category.objects.get(name=array[0])
            cate.icon = icon
            cate.save()
        else:
            Category.objects.create(name=array[0], icon=icon)
        count = 1
        while count < len(array):
            print("sub category count", sub_category_count)
            sub_category_count+=1
            print("total category count", sub_category_count+category_count)
            parent = Category.objects.get(name=array[count - 1])
            if Category.objects.filter(name=array[count]).exists():
                pass
            else:
                Category.objects.create(name=array[count], parent=parent)
            count += 1

    print("population done")


class ImageAssetView(View):
    def post(self, request, *args, **kwargs):
        upload = request.FILES.getlist("upload")
        resp = {}
        for i in upload:
            fss = FileSystemStorage()
            if (
                i.name.split(".")[-1].lower()
                and i.content_type.split("/")[-1].lower() not in allowed_imgs
            ):
                resp[i.name] = "invalid file type"
                continue
            file = fss.save(f"image/{i.name}", i)
            file_url = fss.url(file)
            resp[i.name] = file_url
        return JsonResponse(resp)


def serve(request, path, document_root=None, show_indexes=False):
    path = posixpath.normpath(path).lstrip("/")
    fullpath = Path(safe_join(document_root, path))
    if fullpath.is_dir():
        if show_indexes:
            return directory_index(path, fullpath)
        raise Http404(_("Directory indexes are not allowed here."))
    if not fullpath.exists():
        raise Http404(_("“%(path)s” does not exist") % {"path": fullpath})
    # Respect the If-Modified-Since header.
    statobj = fullpath.stat()
    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or "application/octet-stream"
    response = HttpResponse(content_type=content_type)
    if request.GET.get("width", False) or request.GET.get("height", False):
        img = Image.open(fullpath.open("rb"))
        img = img.resize(
            (
                int(request.GET.get("width", img.size[0])),
                int(request.GET.get("height", img.size[1])),
            )
        )
        img.save(response, content_type.split("/")[-1])
    else:
        if not was_modified_since(
            request.META.get("HTTP_IF_MODIFIED_SINCE"),
            statobj.st_mtime,
            statobj.st_size,
        ):
            return HttpResponseNotModified()
        response = FileResponse(fullpath.open("rb"), content_type=content_type)
    response["Last-Modified"] = http_date(statobj.st_mtime)
    if encoding:
        response["Content-Encoding"] = encoding
    return response


class PopulateProduct(View):
    def get(self, request):
        category = Category.objects.filter(parent=None)
        subcategory = Category.objects.filter(child=None)
        user = ExtendUser.objects.filter(is_seller=True)
        count = 0
        for product in products:
            if count >= 500:
                break
            else:
                count +=1 
            if Product.objects.filter(product_title=product["productTitle"]).exists():
                continue
            else:
                keyword = product["keyword"]
                for word in keyword:
                    if not Keyword.objects.filter(keyword=word).exists():
                        Keyword.objects.create(keyword=word)
                created_product = Product.objects.create(
                    user=random.choice(user),
                    brand=product["brand"],
                    category=random.choice(category),
                    subcategory=random.choice(subcategory),
                    charge_five_percent_vat=product["chargeFivePercentVat"],
                    gender=product["gender"],
                    keyword=keyword,
                    product_title=product["productTitle"],
                    product_weight=product["productWeight"],
                    return_policy=product["returnPolicy"],
                    short_description=product["shortDescription"],
                    warranty=product["warranty"],
                    color=product["color"],
                )
                for option in product["productOptions"]:
                    ProductOption.objects.create(
                        product=created_product,
                        size=option["size"],
                        quantity=option["quantity"],
                        price=option["price"],
                        discounted_price=option["discountedPrice"],
                    )

                if len(product["productOptions"]) < 1:
                    ProductOption.objects.create(
                        product=created_product,
                        size=12,
                        quantity=20,
                        price=34,
                        discounted_price=30,
                    )
                image_url = product["productImageUrl"]
                for i in range(5):
                    ProductImage.objects.create(product=created_product,image_url=image_url,)
                rates = [1, 2, 3, 4, 5]
                user_to_review = ExtendUser.objects.all()

                for i in range(3):
                    Rating.objects.create(
                        product=created_product,
                        rating=random.choice(rates),
                        review="This is a very good product",
                        user=random.choice(user_to_review),
                        likes=random.choice(range(1, 41)),
                        dislikes=random.choice(range(1, 21)),
                    )
        half_products = Product.objects.all().count() / 2
        i = 0
        while i < half_products:
            product_to_promote = random.choice(Product.objects.all())
            if ProductPromotion.objects.filter(product=product_to_promote):
                pass
            else:
                ProductPromotion.objects.create(
                    product=product_to_promote,
                    days=random.choice(range(1, 5)),
                    amount=random.choice(range(1000, 5000)),
                    start_date=timezone.now(),
                )

                i += 1
        return JsonResponse({"status": True, "message": "Products populated"})


class PopulateSellers(View):
    def get(self, request):
        for i in range(5):
            uuD = uuid.uuid4()
            user = get_user_model()(
                username=f"admin{uuD}@kwek.com",
                email=f"admin{uuD}@kwek.com",
                full_name=f"Kwek{i} Admin{i}",
                phone_number=f"{i}{i+1}{i+2}{i+3}{i+4}{i+5}",
                is_verified=True,
                is_seller=True,
            )
            user.set_password("password")
            user.save()
            seller = SellerProfile(
                user=user,
                firstname=f"Kwek{i}",
                lastname=f"Admin{i}",
                phone_number=f"{i}{i+1}{i+2}{i+3}{i+4}{i+5}",
                shop_name=f"Kwekadmin{i}_market",
                shop_url=f"kwekmarket.com/kwekadmin{i}",
                shop_address="Lagos",
                state="Lagos",
                lga="lga",
                accepted_policy=True,
                store_banner_url="https://source.unsplash.com/random/200x200?sig=incrementingIdentifier",
                accepted_vendor_policy=True,
                prefered_id="id",
                prefered_id_url="population.id.url",
                bvn="57587680000",
                bank_name="access",
                bank_sort_code="00445",
                bank_account_number="0076654356",
                bank_account_name="Account Name",
                seller_is_verified=True,
            )

        return JsonResponse(data="Sellers created successfully",safe=False)
        pass
