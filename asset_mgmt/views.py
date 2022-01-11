from json.decoder import JSONDecodeError
from django.shortcuts import render
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

import mimetypes
from PIL import Image
from django.utils.http import http_date, parse_http_date
from django.views.static import directory_index, was_modified_since
from django.utils._os import safe_join
from pathlib import Path
from kwek.vendor_array import data
from market.models import (
    Category, Product, ProductImage, ProductOption, Keyword
)
from users.models import ExtendUser
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
    def post(self, request):
        for array in data:
            if Category.objects.filter(name=array[0]).exists():
                pass
            else:
                Category.objects.create(name=array[0])
            count = 1
            while count < len(array):
                parent = Category.objects.get(name=array[count-1])
                if Category.objects.filter(name=array[count]).exists():
                    pass
                else:
                    Category.objects.create(name=array[count], parent=parent)
                count += 1
        return JsonResponse(
            {
            "status": True,
            "message":"Categories and Subcategories populated"
        }
        )

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
    def post(self, request):
        category = Category.objects.filter(parent=None)
        subcategory = Category.objects.filter(child=None)
        user = ExtendUser.objects.filter(is_seller=True)
        for product in products:
            if Product.objects.filter(product_title=product["productTitle"]).exists():
                continue
            else:
                keyword = []
                keyword.append(product["productTitle"])
                keyword.append(product["brand"])
                keyword.append(product["productOptions"]["size"])
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
                    color=product["color"]
                )
                for option in product["productOptions"]:
                    ProductOption.objects.create(
                        product=created_product,
                        size=option["size"],
                        quantity=option["quantity"],
                        price=option["price"],
                        discounted_price=option["discountedPrice"],
                        option_total_price=option["price"]-option["discountedPrice"]
                    )
                ProductImage.objects.create(
                    product=created_product,
                    image_url="https://source.unsplash.com/random/200x200?sig=incrementingIdentifier"
                )
                ProductImage.objects.create(
                    product=created_product,
                    image_url="https://source.unsplash.com/random/200x200?sig=incrementingIdentifier"
                )
                ProductImage.objects.create(
                    product=created_product,
                    image_url="https://source.unsplash.com/random/200x200?sig=incrementingIdentifier"
                )
                ProductImage.objects.create(
                    product=created_product,
                    image_url="https://source.unsplash.com/random/200x200?sig=incrementingIdentifier"
                )
                ProductImage.objects.create(
                    product=created_product,
                    image_url="https://source.unsplash.com/random/200x200?sig=incrementingIdentifier"
                )

        return JsonResponse( {
            "status": True,
            "message":"Products populated"
        }
        )
        pass