import base64
import datetime
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

import jwt
import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.validators import EmailValidator
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags


from .models import ExtendUser, SellerProfile

logger = logging.getLogger(__name__)


def user_loggedIN(token):
    try:
        dt = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp = int("{}".format(dt["exp"]))
        if time.time() < exp:
            return True
        else:
            return False
    except Exception as e:
        return False


def refresh_user_token(email):
    """
    Generate a new token for the given email if the user exists.

    Args:
        email (str): The email address of the user.

    Returns:
        dict: A dictionary containing the status, token, and message.
    """
    try:
        # Validate that the user exists
        user = ExtendUser.objects.get(email=email)
        current_time = int(time.time())

        # Create a payload for the token
        payload = {
            "user": email,
            "exp": current_time + 151200,  # Token expiry time (e.g., 42 hours)
            "origIat": current_time,
        }

        # Encode the token
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return {
            "status": True,
            "token": token,
            "message": "Token refreshed successfully",
        }
    except ExtendUser.DoesNotExist:
        return {
            "status": False,
            "token": "bow",
            "message": "User with the provided email does not exist",
        }
    except Exception as e:
        return {
            "status": False,
            "token": "rain",
            "message": f"An error occurred: {str(e)}",
        }


def expire_token(token):
    try:
        dt = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if dt["exp"]:
            exp = int("{}".format(dt["exp"]))
            if time.time() > exp:
                return {"status": True, "token": token, "message": "Logged Out"}
            else:
                pt = int(("{}".format(time.time())).split(".")[0])
                payload = {
                    user.USERNAME_FIELD: dt["username"],
                    "exp": int(("{}".format(time.time())).split(".")[0]) + 300,
                    "origIat": int(("{}".format(time.time())).split(".")[0]),
                }

                return {
                    "status": True,
                    "payload": dt,
                    "token": jwt.encode(
                        pt, settings.SECRET_KEY, algorithm="HS256"
                    ),
                    # .decode("utf-8"),
                    "message": "Logged Out",
                }
        else:
            return {"status": False, "token": token, "message": "Invalid Token"}
    except Exception as e:
        return {"status": False, "token": token, "message": "Invalid Token"}


def send_welcome_email(email: str, name: str):
    template_name = "users/welcome.html"
    context = {
        "email": email,
        "name": name,
    }

    html_string = render_to_string(template_name, context)
    send_generic_email_through_PHP([email], html_string, "Welcome to KwekMarket")


def send_verification_email(email: str, name: str) -> Dict[str, Union[bool, str]]:
    """
    Send verification email to user with verification link.

    Args:
        email (str): User's email address
        name (str): User's full name

    Returns:
        dict: Contains status (bool) and message (str)
    """
    try:
        # Input validation
        if not email or not name:
            return {"status": False, "message": "Email and name are required"}

        # Validate email format
        email_validator = EmailValidator()
        try:
            email_validator(email.lower().strip())
        except ValidationError:
            return {"status": False, "message": "Invalid email format"}

        # Get required settings
        secret_key = getattr(settings, "SECRET_KEY", None)
        app_domain = getattr(settings, "APP_DOMAIN", None)

        if not secret_key or not app_domain:
            logger.error("Missing required settings: SECRET_KEY or APP_DOMAIN")
            return {"status": False, "message": "Server configuration error"}

        # Generate JWT token with expiration
        token_payload = {
            "user": email,
            "exp": datetime.utcnow() + timedelta(hours=24),  # 24 hour expiration
            "iat": datetime.utcnow(),
        }

        # Generate token
        try:
            token = jwt.encode(token_payload, secret_key, algorithm="HS256")
        except Exception as e:
            logger.error(f"Token generation failed: {str(e)}")
            return {"status": False, "message": "Failed to generate verification token"}

        # Construct verification link
        verification_link = f"{app_domain}/email_verification/?token={token}"

        # Prepare email template context
        context = {"email": email, "name": name, "link": verification_link}

        try:
            # Render email template
            html_content = render_to_string("users/verification.html", context)

            # Send email
            send_generic_email_through_PHP(
                recipients=[email],
                html_content=html_content,
                subject="Email Verification",
            )

            logger.info(f"Verification email sent successfully to {email}")
            return {"status": True, "message": "Verification email sent successfully"}

        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return {"status": False, "message": "Failed to send verification email"}

    except Exception as e:
        logger.exception(f"Unexpected error in send_verification_email: {str(e)}")
        return {"status": False, "message": "An unexpected error occurred"}


def send_confirmation_email_deprecated(email, full_name):
    username, SECRET_KEY, EMAIL_DOMAIN, APP_DOMAIN, product = (
        email,
        settings.SECRET_KEY,
        settings.EMAIL_BACKEND_DOMAIN,
        settings.APP_DOMAIN,
        "Kwek Market",
    )
    token = jwt.encode({"user": username}, SECRET_KEY, algorithm="HS256")
    # .decode("utf-8")
    token_path = "?token={}".format(token)
    link = "{}/email_verification/{}".format(APP_DOMAIN, token_path)
    payload = {
        "email": email,
        "name": full_name,
        "send_kwek_email": "",
        "product_name": product,
        "api_key": settings.PHPWEB,
        "from_email": settings.KWEK_EMAIL,
        "subject": "Account Verification",
        "event": "email_verification",
        "title": "Verification Email",
        "link": link,
    }

    try:
        status, message = send_email_through_PHP(payload)
        if status:
            return {"status": True, "message": message}
        else:
            return {"status": False, "message": message}
    except Exception as e:
        print(e)
        return {"status": False, "message": e}


def send_password_reset_email(email):
    username, SECRET_KEY, EMAIL_DOMAIN, APP_DOMAIN, product = (
        email,
        settings.SECRET_KEY,
        settings.EMAIL_BACKEND_DOMAIN,
        settings.APP_DOMAIN,
        "Kwek Market",
    )
    token = jwt.encode(
        {
            "user": username,
            "validity": True,
            "exp": int(("{}".format(time.time())).split(".")[0]) + 300,
            "origIat": int(("{}".format(time.time())).split(".")[0]),
        },
        SECRET_KEY,
        algorithm="HS256",
    )
    # .decode("utf-8")
    token_path = "?token={}".format(token)
    link = "{}/change_password/{}".format(APP_DOMAIN, token_path)
    payload = {
        "email": email,
        "send_kwek_email": "",
        "product_name": product,
        "api_key": settings.PHPWEB,
        "from_email": settings.KWEK_EMAIL,
        "subject": "Password Reset",
        "event": "forgot_password",
        "title": "Password Reset",
        "small_text_detail": "You have requested to change your password",
        "link": link,
        "link_keyword": "Change Password",
    }

    try:
        status, message = send_email_through_PHP(payload)
        if status:
            return {"status": True, "message": message}
        else:
            return {"status": False, "message": message}
    except Exception as e:
        return {"status": False, "message": e}


def send_coupon_code(to: List[str], code: str, discount: str):
    """Sends a coupon code email to a list of recipients."""
    context = {
        "code": code,
        "discount": discount,
        "facebook": settings.FACEBOOK_URL,
        "instagram": settings.INSTAGRAM_URL,
        "twitter": settings.TWITTER_URL,
    }

    html_string = render_to_string("users/coupon.html", context)
    return send_generic_email_through_PHP(to, html_string, "Kwek Market Coupon")


def send_email_through_PHP(payload_dictionary):
    url, payload, headers = (
        "http://emailapi.kwekapi.com/",
        json.dumps(payload_dictionary),
        {"Content-Type": "application/json"},
    )
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.json())
        if response.json()["status"]:
            return True, response.json()["message"]
        else:
            return False, "error occured"
    except Exception as e:
        print(e)
        return False, e


def send_generic_email_through_PHP(to: List[str], template: str, subject: str):
    url, payload, headers = (
        "http://emailapi.kwekapi.com/   generic-mail/",
        json.dumps(
            {
                "email_template": get_base64(template),
                "send_kwek_email": "",
                "emails": to,
                "api_key": settings.PHPWEB,
                "from_email": settings.KWEK_EMAIL,
                "subject": subject,
                "product_name": "Kwek Market",
            }
        ),
        {"Content-Type": "application/json"},
    )
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.json()["status"]:
            return True, response.json()["message"]
        else:
            return False, "error occured"
    except Exception as e:
        return False, e


def get_base64(original_string: str) -> str:
    # Convert the string to bytes
    bytes_string = original_string.encode("utf-8")

    # Encode the bytes to Base64
    base64_bytes = base64.b64encode(bytes_string)

    # Convert the Base64 bytes back to a string
    base64_string = base64_bytes.decode("utf-8")

    return base64_string


def send_post_request(url, body):
    """
    Send POST request to external API with proper headers and error handling
    """
    try:
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()  # Raise exception for non-200 status codes

        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"API request failed: {str(e)}"}
    except ValueError as e:
        return {"status": "error", "message": f"Invalid JSON response: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}
