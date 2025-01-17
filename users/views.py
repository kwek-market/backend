import datetime
import json
import time

import jwt
import requests
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import auth
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from users.validate import authenticate_user

from .models import ExtendUser

User = get_user_model()


def get_user_related_models(user):
    related_objects = []
    for rel in User._meta.related_objects:
        related_name = rel.related_name or rel.get_accessor_name()
        related_model = rel.related_model
        related_objects.append((related_name, related_model))
    return related_objects


def delete_user_and_related_records(request):
    if request.method != "DELETE":
        return JsonResponse(
            {"status": "error", "message": "Invalid request method."}, status=405
        )

    try:
        auth = authenticate_user(request.headers.get("Authorization"))
        user = auth["user"]

        related_models = get_user_related_models(user)

        if not auth["status"]:
            return JsonResponse(
                {"status": auth["status"], "message": auth["message"]}
            )

        with transaction.atomic():  # Ensure atomicity
            for related_name, model in related_models:
                related_manager = getattr(user, related_name, None)
                if related_manager is None:
                    continue  # Skip if the related manager is not found

                # Handle different relationship types
                if hasattr(related_manager, "all"):  # Many-to-one or many-to-many
                    related_manager.all().delete()
                else:  # One-to-one or foreign key
                    related_instance = related_manager
                    if related_instance:
                        related_instance.delete()

            user.delete()  # Finally, delete the user

        return JsonResponse(
            {
                "status": "success",
                "message": "User and all related records deleted successfully.",
            },
            status=200,
        )
    except User.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "User not found."}, status=404
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def verify_email(request):
    r_user = request.user
    if request.method == "GET":
        token = request.GET.get("token", None)
        if token is None:
            context = {
                "status": "false",
                "Message": "E-mail Verification Failed",
                "token": "No Token",
                "alert_type": "danger",
            }
            return render(request, "kwek_auth/email_verification.html", context)
        else:
            username = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])[
                "user"
            ]
            try:
                user = ExtendUser.objects.get(email=username)
                user.is_verified = True
                user.save()
                # return CreateUser(status=True, message = "Verification Successful")
                context = {
                    "status": "True",
                    "Message": "E-mail Verification was Successful",
                    "token": token,
                    "alert_type": "success",
                }
                return render(request, "kwek_auth/email_verification.html", context)
                # return redirect("https://{}/login".format(settings.DOMAIN))
            except Exception as e:
                context = {
                    "status": "false",
                    "Message": "{}".format(e),
                    "token": token,
                    "alert_type": "danger",
                }
                return render(request, "kwek_auth/email_verification.html", context)
                # return redirect("https://{}/not_login".format(settings.DOMAIN))


def home_redirect(request):
    return redirect("https://{}/".format(settings.DOMAIN))
