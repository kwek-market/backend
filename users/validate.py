import re
from django.contrib.auth.models import User, auth
from django.contrib.auth import get_user_model
from .models import ExtendUser

def validate_email(email):
    User = get_user_model()
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if(re.search(regex, email)):
        if ExtendUser.objects.filter(email=email).exists():
          return {"status": False, "message": "E-mail Already in use"}
        else:
            return {"status": True, "message": "Valid Email"}  
    else:
        return {"status": False, "message": "Enter Valid E-mail"}


def validate_passwords(password1, password2):
    if len(password1) < 8:
        return {"status": False, "message": "Password is should not be less than 8 characters"}
    elif not any(char.isdigit() for char in password1):
        return {"status": False, "message": "Password should contain numerical character"}
    elif password1 != password2:
        return {"status": False, "message": "Passwords do not match"}
    else:
        return {"status": True, "message": "Valid Password"}


def validate_user_passwords(new_password):
    if len(new_password) < 8:
        return {"status": False, "message": "Password is should not be less than 8 characters"}
    elif not any(char.isdigit() for char in new_password):
        return {"status": False, "message": "Password should contain numerical character"}
    else:
        return {"status": True, "message": "Valid Password"}