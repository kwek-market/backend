from django.shortcuts import render
from django.http import JsonResponse
from .pusher import PushToClient

# Create your views here.

def pusher_test(request):
    return render(request, "market/index.html")

def trigger_push(request):
    for i in range(100):
        PushToClient('my-channel',{'message': 'hello world, count {}'.format(i)})
    return JsonResponse({"status": True,"message":"Notification Triggered"})
