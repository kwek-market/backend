from typing import List
import jwt
import time
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import datetime
import requests
import json
import base64
from .models import ExtendUser, SellerProfile
from django.template.loader import render_to_string


def user_loggedIN(token):
    try:
        dt = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        exp = int("{}".format(dt['exp']))
        if time.time() < exp:
            return True
        else:
            return False
    except Exception as e:
        return False


def refresh_user_token(email):
    ct = int(('{}'.format(time.time())).split('.')[0])
    payload = {user.USERNAME_FIELD: email, 'exp': ct + 151200, 'origIat': ct}
    token = jwt.encode(payload, settings.SECRET_KEY,
                       algorithm='HS256').decode('utf-8')
    return {"status": False, "token": token, "message": "New Token"}


def expire_token(token):
    try:
        dt = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if dt['exp']:
            exp = int("{}".format(dt['exp']))
            if time.time() > exp:
                return {"status": True, "token": token, "message": "Logged Out"}
            else:
                pt = int(('{}'.format(time.time())).split('.')[0])
                payload = {
                    user.USERNAME_FIELD: dt['username'],
                    'exp': int(('{}'.format(time.time())).split('.')[0]) + 300,
                    'origIat': int(('{}'.format(time.time())).split('.')[0])
                }

                return {"status": True, "payload": dt, "token": jwt.encode(pt, settings.SECRET_KEY, algorithm='HS256').decode('utf-8'), "message": "Logged Out"}
        else:
            return {"status": False, "token": token, "message": "Invalid Token"}
    except Exception as e:
        return {"status": False, "token": token, "message": "Invalid Token"}

def send_welcome_email(email:str, name:str):
    template_name = 'users/welcome.html'
    context = {
    'email': email,
    'name': name,
    }

    html_string = render_to_string(template_name, context)
    send_generic_email_through_PHP([email], html_string, "Welcome to KwekMarket")

def send_verification_email(email:str, name:str):
    username, SECRET_KEY,APP_DOMAIN = email, settings.SECRET_KEY, settings.APP_DOMAIN
    token = jwt.encode({'user': username}, SECRET_KEY,
                       algorithm='HS256').decode("utf-8")
    token_path = "?token={}".format(token)
    link = "{}/email_verification/{}".format(APP_DOMAIN, token_path)
    template_name = 'users/verification.html'
    context = {
    'email': email,
    'name': name,
    'link': link
    }

    html_string = render_to_string(template_name, context)
    send_generic_email_through_PHP([email], html_string, "Email Verification")

def send_confirmation_email_deprecated(email,full_name):
    username, SECRET_KEY, EMAIL_DOMAIN,APP_DOMAIN,product = email, settings.SECRET_KEY, settings.EMAIL_BACKEND_DOMAIN, settings.APP_DOMAIN,"Kwek Market"
    token = jwt.encode({'user': username}, SECRET_KEY,
                       algorithm='HS256').decode("utf-8")
    token_path = "?token={}".format(token)
    link = "{}/email_verification/{}".format(APP_DOMAIN, token_path)
    payload = {
        "email": email,"name": full_name,"send_kwek_email": "","product_name": product,"api_key": settings.PHPWEB,
        "from_email": settings.KWEK_EMAIL,"subject": 'Account Verification',"event": "email_verification",
        "title": 'Verification Email', "link": link
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


def send_password_reset_email(email):
    username, SECRET_KEY, EMAIL_DOMAIN,APP_DOMAIN,product = email, settings.SECRET_KEY, settings.EMAIL_BACKEND_DOMAIN, settings.APP_DOMAIN,"Kwek Market"
    token = jwt.encode({'user': username, "validity": True, 'exp': int(('{}'.format(time.time())).split('.')[0]) + 300,
                        'origIat': int(('{}'.format(time.time())).split('.')[0])},
                       SECRET_KEY,
                       algorithm='HS256').decode('utf-8')
    token_path = "?token={}".format(token)
    link = "{}/change_password/{}".format(APP_DOMAIN, token_path)
    payload = {
        "email": email,"send_kwek_email": "","product_name": product,"api_key": settings.PHPWEB,
        "from_email": settings.KWEK_EMAIL,"subject": 'Password Reset',"event": "forgot_password",
        "title": 'Password Reset',"small_text_detail": "You have requested to change your password",
        "link": link,"link_keyword": "Change Password"
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
    
def send_coupon_code(to: List[str], code:str):
    template_name = 'users/coupon.html'
    context = {
    'code': code,
    'facebook': settings.FACEBOOK_URL,
    'instagram': settings.INSTAGRAM_URL,
    'twitter': settings.TWITTER_URL
    }

    html_string = render_to_string(template_name, context)
    send_m = send_generic_email_through_PHP(to, html_string, "Kwek Market Coupon")





def send_email_through_PHP(payload_dictionary):
    url, payload, headers = "http://emailapi.kwekapi.com/", json.dumps(
        payload_dictionary), {'Content-Type': 'application/json'}
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.json())
        if response.json()["status"]:
            return True,response.json()['message']
        else:
            return False, "error occured"
    except Exception as e:
        print(e)
        return False,e 
    

def send_generic_email_through_PHP(to:List[str], template:str, subject:str):
    url, payload, headers = "http://emailapi.kwekapi.com/generic-mail/", json.dumps(
        {   "email_template": get_base64(template),
            "send_kwek_email": "",
            "emails": to,
            "api_key": settings.PHPWEB,
            "from_email": settings.KWEK_EMAIL,
            "subject": subject,
            "product_name": "Kwek Market",
         }), {'Content-Type': 'application/json'}
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.json())
        if response.json()["status"]:
            return True,response.json()['message']
        else:
            return False, "error occured"
    except Exception as e:
        print(e)
        return False,e 
    

def get_base64(original_string:str) ->str :
    # Convert the string to bytes
    bytes_string = original_string.encode('utf-8')

    # Encode the bytes to Base64
    base64_bytes = base64.b64encode(bytes_string)

    # Convert the Base64 bytes back to a string
    base64_string = base64_bytes.decode('utf-8')

    return base64_string



