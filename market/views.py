from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .jobs import completeDelivery, unpromote
from .pusher import SendEmailNotification, push_to_client

# Create your views here.


def pusher_test(request):
    return render(request, "market/index.html")


def trigger_push(request):
    for i in range(100):
        push_to_client("my-channel", {"message": "hello world, count {}".format(i)})
        notification = SendEmailNotification("gregoflash05@gmail.com")
        if i % 20 == 0:
            notification.send_only_one_paragraph(
                "Paragraph", "This is the one paragraph"
            )
            notification.send_html_content(
                "Paragraph",
                "<div>This is the html content with <a href='google.com'>this link</a></div>",
            )
    return JsonResponse({"status": True, "message": "Notification Triggered"})


@method_decorator(csrf_exempt, name="dispatch")
class UnpromoteView(View):
    def post(self, request, *args, **kwargs):
        try:
            unpromote()  # Call the unpromote task
            return JsonResponse(
                {"message": "Unpromote task executed successfully."}, status=200
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class CompleteDeliveryView(View):
    def post(self, request, *args, **kwargs):
        try:
            completeDelivery()  # Call the completeDelivery task
            return JsonResponse(
                {"message": "Complete delivery task executed successfully."}, status=200
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
