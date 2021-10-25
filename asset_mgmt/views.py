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
import posixpath

# Create your views here.

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
