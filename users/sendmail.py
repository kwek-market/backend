import jwt
import time
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import datetime;

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
    payload = { user.USERNAME_FIELD: email,'exp': ct + 151200,'origIat': ct}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
    return {"status": False, "token" : token, "message" : "New Token"}


def expire_token(token):
    try:
        dt = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if dt['exp']:
            exp = int("{}".format(dt['exp']))
            if time.time() > exp:
                return {"status": True, "token" : token, "message" : "Logged Out"}
            else:
                pt = int(('{}'.format(time.time())).split('.')[0])
                payload = {
                    user.USERNAME_FIELD: dt['username'],
                    'exp': int(('{}'.format(time.time())).split('.')[0]) + 300,
                    'origIat': int(('{}'.format(time.time())).split('.')[0])
                }
                
                return {"status": True, "payload":dt, "token" : jwt.encode(pt, settings.SECRET_KEY, algorithm='HS256').decode('utf-8'), "message" : "Logged Out"}
        else:
            return {"status": False, "token" : token, "message" : "Invalid Token"}
    except Exception as e:
        return {"status": False, "token" : token, "message" : "Invalid Token"}


def send_confirmation_email(email):
    username, SECRET_KEY, DOMAIN= email, settings.SECRET_KEY, settings.DOMAIN
    token = jwt.encode({'user': username}, SECRET_KEY,
                       algorithm='HS256').decode('utf-8')

    token_path = "?token={}".format(token)
    context = {
        'small_text_detail': 'Thank you for '
                             'creating an account. '
                             'Please verify your email '
                             'address to set up your account.',
        'email': email,
        'domain': DOMAIN,
        'token': token_path,
        'button_name': "Verify Account",
        'title': "Email Verification",
        'path': "verify/",
    }
    # locates our email.html in the templates folder
    msg_html = render_to_string('users/email.html', context)
    # message = Mail(
    #     # the email that sends the confirmation email
    #     from_email=settings.KWEK_EMAIL,
    #     to_emails=[email],  # list of email receivers
    #     subject='Account Verification',  # subject of your email
    #     html_content=msg_html)
    from_email=settings.KWEK_EMAIL
    subject='Account Verification'
    newsletter_txt = strip_tags(msg_html)
    # html_template = get_template('users/email.html').render()
    message = EmailMultiAlternatives(subject, newsletter_txt, from_email, [email])
    message.attach_alternative(msg_html, 'text/html')
    # message.send()
    try:
        if message.send():
            return {"status" : True, "message" : "Email sent", "email" : msg_html}
        else:
            return {"status" : False, "message" : "Email not sent"}
    except Exception as e:
        return {"status" : False, "message" : e}



def send_password_reset_email(email):
    username, SECRET_KEY, DOMAIN= email, settings.SECRET_KEY, settings.DOMAIN
    token = jwt.encode({'user': username, "validity" : True, 'exp': int(('{}'.format(time.time())).split('.')[0]) + 300,
                    'origIat': int(('{}'.format(time.time())).split('.')[0])},
                     SECRET_KEY,
                       algorithm='HS256').decode('utf-8')
    token_path = "?token={}".format(token)
    context = {
        'small_text_detail': 'Please click '
                             'the button below '
                             'to change your Password. ',
        'email': email,
        'domain': DOMAIN,
        'token': token_path,
        'button_name': "Reset Password",
        'title': "Password Reset",
        'path': "change_password/",
    }
    msg_html = render_to_string('users/email.html', context)
    from_email=settings.KWEK_EMAIL
    subject='Password Reset'
    newsletter_txt = strip_tags(msg_html)
    message = EmailMultiAlternatives(subject, newsletter_txt, from_email, [email])
    message.attach_alternative(msg_html, 'text/html')
    try:
        if message.send():
            return {"status" : True, "message" : "Email sent", "email" : msg_html}
        else:
            return {"status" : False, "message" : "Email not sent"}
    except Exception as e:
        return {"status" : False, "message" : e}