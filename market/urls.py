from django.urls import path
from . import views

urlpatterns = [
    path("pusher/", views.pusher_test, name = "Pusher test"),
    path("trigger/", views.trigger_push, name = "Pusher Trigger"),
    path('trigger/unpromote/', views.UnpromoteView.as_view(), name='trigger-unpromote'),
    path('trigger/complete-delivery/', views.CompleteDeliveryView.as_view(), name='trigger-complete-delivery'),
]
