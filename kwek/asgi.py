# """
# ASGI config for kwek project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# from channels.routing import ProtocolTypeRouter

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kwek.settings')

# django_asgi_app = get_asgi_application()


# #its important to make all other imports below this comment
# import socketio
# from notifications.views import sio

# application = socketio.ASGIApp(sio, django_asgi_app)
