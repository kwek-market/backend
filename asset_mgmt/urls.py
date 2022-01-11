from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from asset_mgmt.views import ImageAssetView, FileAssetView, PopulateCategory, PopulateProduct

urlpatterns = [
    path("image", csrf_exempt(ImageAssetView.as_view())),
    path("file", csrf_exempt(FileAssetView.as_view())),
    path("category", csrf_exempt(PopulateCategory.as_view())),
    path("product", csrf_exempt(PopulateProduct.as_view()))
]
