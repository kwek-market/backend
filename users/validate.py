import re
import time
from email.mime import audio

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, auth
from jwt.exceptions import DecodeError, ExpiredSignatureError

from .models import ExtendUser


def validate_email(email):
    User = get_user_model()
    regex = "^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$"
    if re.search(regex, email):
        if ExtendUser.objects.filter(email=email).exists():
            return {"status": False, "message": "E-mail Already in use"}
        else:
            return {"status": True, "message": "Valid Email"}
    else:
        return {"status": False, "message": "Enter Valid E-mail"}


def validate_passwords(password1, password2):
    if len(password1) < 8:
        return {
            "status": False,
            "message": "Password is should not be less than 8 characters",
        }
    elif not any(char.isdigit() for char in password1):
        return {
            "status": False,
            "message": "Password should contain numerical character",
        }
    elif password1 != password2:
        return {"status": False, "message": "Passwords do not match"}
    else:
        return {"status": True, "message": "Valid Password"}


def validate_user_passwords(new_password):
    if len(new_password) < 8:
        return {
            "status": False,
            "message": "Password is should not be less than 8 characters",
        }
    elif not any(char.isdigit() for char in new_password):
        return {
            "status": False,
            "message": "Password should contain numerical character",
        }
    else:
        return {"status": True, "message": "Valid Password"}


def authenticate_user(token: str):
    try:
        # Decode the token once
        dt = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        # Check expiration time
        exp = dt.get("exp")
        if exp and int(time.time()) < exp:
            email = dt.get("username")
            if not email:
                return {
                    "status": False,
                    "message": "Invalid token structure",
                    "user": None,
                }

            user = ExtendUser.objects.get(email=email)
            return {"status": True, "message": "authenticated", "user": user}
        else:
            return {"status": False, "message": "token expired", "user": None}

    except ExpiredSignatureError:
        return {"status": False, "message": "token expired", "user": None}
    
    except DecodeError:
        return {
            "status": False,
            "message": "invalid authentication token",
            "user": None,
        }
    except ExtendUser.DoesNotExist:
        return {"status": False, "message": "user not found", "user": None}
    except Exception as e:
        return {
            "status": False,
            "message": str(e),
            "user": None,
        }


def authenticate_admin(token: str):
    auth = authenticate_user(token)
    user = auth["user"]
    if user.is_admin:
        return {"status": True, "message": "authenticated", "user": user}
    else:
        return {"status": False, "message": "Not an admin", "user": ExtendUser()}
