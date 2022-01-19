from django.urls import path
from . import views

urlpatterns = [
    path("pusher/", views.pusher_test, name = "Pusher test"),
    path("trigger/", views.trigger_push, name = "Pusher Trigger"),
]