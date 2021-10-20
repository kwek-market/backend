from django.shortcuts import render, get_object_or_404
import json	
from django.http import Http404
import json
import requests
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, auth
from django.http import HttpResponse
from django.http import JsonResponse
import jwt
from .models import ExtendUser
from django.contrib.auth import authenticate
import time
import datetime
from django.conf import settings


def verify_email(request):
    r_user = request.user
    if request.method == "GET":
        token = request.GET.get('token', None)
        if token is None:
            context ={'status' : "false", 'Message' : "E-mail Verification Failed", 'token' : "No Token", 'alert_type' : "danger"}
            return render(request, "kwek_auth/email_verification.html", context)
        else:
            username = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])["user"]
            try:
                user = ExtendUser.objects.get(email=username)
                user.is_verified = True
                user.save()
                # return CreateUser(status=True, message = "Verification Successful")
                context ={'status' : "True", 'Message' : "E-mail Verification was Successful", 'token' : token, 'alert_type' : "success"}
                return render(request, "kwek_auth/email_verification.html", context)
                # return redirect("https://{}/login".format(settings.DOMAIN))
            except Exception as e:
                context ={'status' : "false", 'Message' : "{}".format(e), 'token' : token, 'alert_type' : "danger"}
                return render(request, "kwek_auth/email_verification.html", context)
                # return redirect("https://{}/not_login".format(settings.DOMAIN))


def home_redirect(request):
    # return redirect("https://{}/".format(settings.DOMAIN))
    return redirect("https://google.com")
        
