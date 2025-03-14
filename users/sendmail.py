import base64
import datetime
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.validators import EmailValidator
from django.http import HttpRequest
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags

User = get_user_model()

from .models import ExtendUser, SellerProfile

logger = logging.getLogger(__name__)


def get_domain(request=None):
    """
    Get the domain from the current request or server settings.
    Falls back to a default if neither is available.
    """
    try:
        if request:
            current_site = get_current_site(request)
            print("we are talkinf about the current site", current_site)
            return current_site.domain

        # If no request is available, try to get from settings
        from django.conf import settings

        if hasattr(settings, "ALLOWED_HOSTS") and settings.ALLOWED_HOSTS:
            # Use the first non-wildcard allowed host
            for host in settings.ALLOWED_HOSTS:
                if host and host != "*":
                    return host

        # Fallback to default domain
        return "localhost:8000"
    except Exception as e:
        logger.warning(f"Failed to detect domain: {str(e)}")
        return "localhost:8000"


def validate_email_address(email: str) -> Dict[str, Union[bool, str]]:
    """
    Performs comprehensive email validation including syntax and domain verification.

    Args:
        email (str): Email address to validate

    Returns:
        dict: Contains status and detailed message
            {
                'is_valid': bool,
                'message': str
            }
    """
    # Initialize response
    response = {"is_valid": False, "message": ""}

    # Basic structure check
    if not email or not isinstance(email, str):
        response["message"] = "Email address cannot be empty"
        return response

    # Length check
    if len(email) > 254:
        response["message"] = "Email address is too long"
        return response

    # Regex pattern for email validation
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        response["message"] = "Invalid email format"
        return response

    # Split email into local and domain parts
    try:
        local_part, domain = email.rsplit("@", 1)
    except ValueError:
        response["message"] = "Invalid email format"
        return response

    # Check local part length
    if len(local_part) > 64:
        response["message"] = "Local part of email is too long"
        return response

    # Verify domain has MX record
    try:
        dns.resolver.resolve(domain, "MX")
        response["is_valid"] = True
        response["message"] = "Email address is valid"
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        response["message"] = f"Domain {domain} does not have valid mail servers"
    except Exception as e:
        logger.error(f"DNS lookup error for {domain}: {str(e)}")
        # If DNS lookup fails, we'll still accept the email if it passed other checks
        response["is_valid"] = True
        response["message"] = "Email format is valid (domain verification unavailable)"

    return response


def validate_email_payload(payload: dict) -> Dict[str, Union[bool, str]]:
    """
    Validates the complete email payload before sending.

    Args:
        payload (dict): Email payload dictionary containing email details

    Returns:
        dict: Validation results with status and message
    """
    required_fields = ["emails", "api_key", "from_email", "subject"]

    # Check for required fields
    for field in required_fields:
        if field not in payload:
            return {"status": False, "message": f"Missing required field: {field}"}

    # Validate recipient emails
    if not payload["emails"] or not isinstance(payload["emails"], list):
        return {"status": False, "message": "Invalid or empty recipient email list"}

    for email in payload["emails"]:
        validation_result = validate_email_address(email)
        if not validation_result["is_valid"]:
            return {"status": False, "message": f"Invalid recipient email: {email}"}

    # Validate sender email
    sender_validation = validate_email_address(payload["from_email"])
    if not sender_validation["is_valid"]:
        return {
            "status": False,
            "message": f'Invalid sender email: {payload["from_email"]}',
        }

    # Validate API key format (adjust pattern as needed)
    if not re.match(r"^[a-zA-Z0-9_-]+$", payload["api_key"]):
        return {"status": False, "message": "Invalid API key format"}

    return {"status": True, "message": "Payload validation successful"}


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
        user = User.objects.get(email=email)
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
    except User.DoesNotExist:
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
                    "token": jwt.encode(pt, settings.SECRET_KEY, algorithm="HS256"),
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


def get_setting(name, default=None):
    """Helper function to fetch settings with error handling."""
    value = getattr(settings, name, default)
    if value is None:
        logger.error(f"Missing required setting: {name}")
    return value


def generate_jwt_token(email: str, secret_key: str) -> str:
    """Generates a JWT token with a 24-hour expiration."""
    try:
        payload = {
            "user": email,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, secret_key, algorithm="HS256")
    except jwt.PyJWTError as e:
        logger.error(f"JWT token generation failed: {e}")
        return None


def render_email_template(template_name: str, context: dict) -> str:
    """Renders an email template and returns the HTML content."""
    try:
        return render_to_string(template_name, context)
    except Exception as e:
        logger.error(f"Failed to render email template '{template_name}': {e}")
        return None


def send_verification_email(
    email: str, name: str, request=None
) -> Dict[str, Union[bool, str]]:
    """
    Sends a verification email with a secure link.

    Args:
        email (str): Recipient's email.
        name (str): Recipient's name.
        request (HttpRequest, optional): Request object for domain detection.

    Returns:
        dict: Contains 'status' (bool) and 'message' (str).
    """
    if not email or not name:
        return {"status": False, "message": "Email and name are required"}

    try:
        EmailValidator()(email.lower().strip())
    except ValidationError:
        return {"status": False, "message": "Invalid email format"}

    secret_key = get_setting("SECRET_KEY")
    if not secret_key:
        return {"status": False, "message": "Server configuration error"}

    domain = (
        request.get_host()
        if request
        else get_setting("DEFAULT_DOMAIN", "your-default-domain.com")
    )
    scheme = "https" if request and request.is_secure() else "http"

    token = generate_jwt_token(email, secret_key)
    if not token:
        return {"status": False, "message": "Failed to generate verification token"}

    verification_link = f"{scheme}://{domain}/email_verification/?token={token}"
    email_context = {"email": email, "name": name, "link": verification_link}

    html_content = render_email_template("users/verification.html", email_context)
    if not html_content:
        return {"status": False, "message": "Error generating email content"}

    email_payload = {
        "email_template": json.dumps(html_content),  # Ensures JSON-safe encoding
        "send_kwek_email": "",
        "emails": [email],
        "api_key": get_setting("PHPWEB"),
        "from_email": get_setting("KWEK_EMAIL"),
        "subject": "Email Verification",
        "product_name": "Kwek Market",
    }

    send_email = send_email_through_PHP(email_payload)
    print("I am statusessssing the mail sent", send_email["status"] , "and the message sent is also being tracked here", send_email["message"])
    return {"status": send_email["status"], "message": send_email["message"]}

    # if send_status:
    #     logger.info(f"Verification email sent successfully to {email}")
    #     return {"status": send_status, "message": send_message}
    # else:
    #     logger.error(f"Failed to send verification email: {send_message}")
    #     return {"status": send_status, "message": send_message}


def send_confirmation_email_deprecated(email, full_name, request):
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
    """
    Sends an email via the PHP email API.

    Args:
        payload_dictionary (dict): The payload containing email details.

    Returns:
        dict: {"status": bool, "message": str}
    """
    url = "http://emailapi.kwekapi.com/"
    headers = {"Content-Type": "application/json"}

    try:
        # Convert payload to JSON
        payload = json.dumps(payload_dictionary)

        # Send POST request
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        print(payload_dictionary, "mailss")

        # Ensure valid JSON response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            logger.error("Invalid JSON response received from email API")
            return {"status": False, "message": "Invalid response from email server"}

        # Check API response status
        if response_data.get("status"):
            return {
                "status": True,
                "message": response_data.get("message", "Email sent successfully"),
            }
        else:
            error_message = response_data.get("message", "Unknown error occurred")
            logger.error(f"Email API responded with error: {error_message}")
            return {"status": False, "message": error_message}

    except requests.Timeout:
        logger.error("Email API request timed out")
        return {"status": False, "message": "Email service timeout"}

    except requests.RequestException as e:
        logger.error(f"Email API request failed: {str(e)}")
        return {"status": False, "message": "Failed to connect to email service"}

    except Exception as e:
        logger.exception(f"Unexpected error in send_email_through_PHP: {str(e)}")
        return {"status": False, "message": "An unexpected error occurred"}


def send_generic_email_through_PHP(to: List[str], template: str, subject: str):
    url, payload, headers = (
        "http://emailapi.kwekapi.com/generic-mail/",
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
        response_data = response.json()
        return {"status": response_data["status"], "message": response_data["message"]}
    except Exception as e:
        return {"status": False, "message": str(e)}


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
