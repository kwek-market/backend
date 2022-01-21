from django.shortcuts import render
from django.http import JsonResponse
from .pusher import push_to_client, SendEmailNotification

# Create your views here.

def pusher_test(request):
    return render(request, "market/index.html")

def trigger_push(request):
    for i in range(100):
        push_to_client('my-channel',{'message': 'hello world, count {}'.format(i)})
        notification = SendEmailNotification("gregoflash05@gmail.com")
        if i%20 == 0:
            notification.send_only_one_paragraph("Paragraph","This is the one paragraph")
            notification.send_html_content("Paragraph","<div>This is the html content with <a href='google.com'>this link</a></div>")
    return JsonResponse({"status": True,"message":"Notification Triggered"})
