import pusher
from decouple import config
from users.models import ExtendUser
from django.conf import settings
from users.sendmail import send_email_through_PHP

pusher_client = pusher.Pusher(
    app_id=config("PUSHER_APP_ID"),
    key=config("PUSHER_KEY"),
    secret=config("PUSHER_SECRET"),
    cluster=config("PUSHER_CLUSTER"),
    ssl=True,
)


def PushToClient(channel: str, data: dict):
    pusher_client.trigger(channel, channel, data)


class SendEmailNotification():
    def __init__(self, email):
        self.user = ExtendUser.objects.get(email=email)
        self.event = "notification"
        self.product = "Kwek Market"

    def send_only_one_paragraph(self, title, paragraph):
        payload = {
            "email": self.user.email,
            "name": self.user.full_name,
            "send_kwek_email": "",
            "product_name": self.product,
            "api_key": settings.PHPWEB,
            "from_email": settings.KWEK_EMAIL,
            "subject": title,
            "event": self.event,
            "notification_title": title,
            "no_html_content": paragraph,
            "html_content": "",
        }

        try:
            status,message = send_email_through_PHP(payload)
            if status:
                return {"status": True, "message": message}
            else:
                return {"status": False, "message": message}
        except Exception as e:
            print(e)
            return {"status": False, "message": e}

    def send_html_content(self, title, html_content):
        payload = {
            "email": self.user.email,
            "name": self.user.full_name,
            "send_kwek_email": "",
            "product_name": self.product,
            "api_key": settings.PHPWEB,
            "from_email": settings.KWEK_EMAIL,
            "subject": title,
            "event": self.event,
            "notification_title": title,
            "no_html_content": "",
            "html_content": html_content,
        }

        try:
            status,message = send_email_through_PHP(payload)
            if status:
                return {"status": True, "message": message}
            else:
                return {"status": False, "message": message}
        except Exception as e:
            print(e)
            return {"status": False, "message": e}
