from typing import Dict, List
import graphene
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from market.models import Cart, Wishlist
import uuid

from market.mutation import verify_cart
from market.pusher import SendEmailNotification, push_to_client
from notifications.models import Message, Notification
from wallet.models import StoreDetail, Wallet
from .validate import validate_email, validate_passwords, validate_user_passwords, authenticate_user, authenticate_admin
from .sendmail import (
    send_confirmation_email,
    send_generic_email_through_PHP,
    user_loggedIN,
    expire_token,
    send_password_reset_email,
    refresh_user_token,
)
from .models import ExtendUser, SellerProfile
from django.contrib.auth import authenticate
from graphql_jwt.shortcuts import create_refresh_token
import time
from .send_post import send_post_request
from django.contrib.auth.hashers import check_password
from .model_object_type import UserType, SellerProfileType
from django.template import Template, Context


class CreateUser(graphene.Mutation):
    sender = settings.EMAIL_HOST_USER
    status = graphene.Boolean()
    message = graphene.String()
    email_text = graphene.String()

    class Arguments:
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)
        full_name = graphene.String(required=True)
        email = graphene.String(required=True)
        # status = False

    @staticmethod
    def mutate(self, info, password1, password2, email, full_name):
        email = email.lower()
        user = get_user_model()(
            username=email,
            email=email,
            full_name=full_name,
        )

        if validate_email(email)["status"] == False:
            return CreateUser(status=False, message=validate_email(email)["message"])
        elif validate_passwords(password1, password2)["status"] == False:
            return CreateUser(
                status=False,
                message=validate_passwords(password1, password2)["message"],
            )
        else:
            sen_m = send_confirmation_email(email, full_name)
            if sen_m["status"] == True:
                user.set_password(password1)
                user.save()
                Cart.objects.create(user=user)
                Wishlist.objects.create(user=user)
                Notification.objects.create(user=user)
                return CreateUser(
                    status=True,
                    message="Successfully created account for, {}".format(
                        user.username
                    ),
                )
            else:
                # raise GraphQLError("Email Verification not sent")
                return CreateUser(status=False, message=sen_m["message"])
        # raise Exception('Invalid Link!')


class ResendVerification(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    email_text = graphene.String()

    class Arguments:
        email = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, email):
        f_user = ExtendUser.objects.get(email=email)
        sen_m = send_confirmation_email(email, f_user.full_name)
        if sen_m["status"] == True:
            return ResendVerification(
                status=True,
                message="Successfully sent email to {}".format(email),
            )
        else:
            # raise GraphQLError("Email Verification not sent")
            return ResendVerification(status=False, message=sen_m["message"])


class VerifyUser(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, token):
        username = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])["user"]
        try:
            user = ExtendUser.objects.get(email=username)
            user.is_verified = True
            user.save()
            return CreateUser(status=True, message="Verification Successful")
        except Exception as e:
            return CreateUser(status=False, message=e)


class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    message = graphene.String()
    token = graphene.String()
    status = graphene.Boolean()
    payload = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        ip = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, email, password, ip):
        email = email.lower()
        user = authenticate(username=email, password=password)
        error_message = "Invalid login credentials"
        success_message = "You logged in successfully."
        verification_error = "Your email is not verified"

        if user:
            if user.is_verified:
                ct = int(("{}".format(time.time())).split(".")[0])
                payload = {
                    user.USERNAME_FIELD: email,
                    "exp": ct + 151200,
                    "origIat": ct,
                }
                # payload = jwt_payload(user)
                # time_diff = time.time() - payload['exp']
                # load_p = int("{}".format(payload['exp']))
                # payload['exp'] = load_p + 3600
                # f_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
                # dt = jwt.decode(f_token, settings.SECRET_KEY, algorithms=['HS256'])
                # exp = dt['exp']
                # dt['exp'] = exp + 3600
                # token = jwt.encode(dt, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
                token = jwt.encode(
                    payload, settings.SECRET_KEY, algorithm="HS256"
                ).decode("utf-8")
                # token = get_token(user)
                refresh_token = create_refresh_token(user)
                verify_cart(ip, token)
                if Notification.objects.filter(user=user).exists():
                    notification = Notification.objects.get(
                        user=user
                    )
                else:
                    notification = Notification.objects.create(
                        user=user
                    )
                notification_message = Message.objects.create(
                    notification=notification,
                    message=f"Login successful",
                    subject="New Login"
                )
                notification_info = {"notification":str(notification_message.notification.id),
                "message":notification_message.message, 
                "subject":notification_message.subject}
                push_to_client(user.id, notification_info)
                email_send = SendEmailNotification(user.email)
                email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)
                return LoginUser(
                    user=user,
                    status=True,
                    token=token,
                    message=success_message,
                    payload=payload,
                )
            return LoginUser(status=False, message=verification_error)
        return LoginUser(status=False, message=error_message)


class VerifyToken(graphene.Mutation):
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String()

    @staticmethod
    def mutate(self, info, token):
        auth = authenticate_user(token)
        if auth["status"]:
            return VerifyToken(status=auth["status"], message=auth["message"])
        else:
            return VerifyToken(status=auth["status"], message=auth["message"])

class RevokeToken(graphene.Mutation):
    message = graphene.String()
    token = graphene.String()
    payload = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String()

    @staticmethod
    def mutate(self, info, token):
        result = expire_token(token)
        if result["status"]:
            return RevokeToken(
                status=True,
                message=result["message"],
                token=result["token"],
                payload=result["payload"],
            )
        else:
            return RevokeToken(
                status=True, message=result["message"], token=result["token"]
            )


class RefreshToken(graphene.Mutation):
    message = graphene.String()
    token = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String()
        email = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, token, email):
        result = refresh_user_token(email)
        try:
            if result["status"]:
                return RefreshToken(
                    status=True, message=result["message"], token=result["token"]
                )
            else:
                return RefreshToken(status=False)
        except:
            return RefreshToken(status=False)


class SendPasswordResetEmail(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        email = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, email):
        sen_m = send_password_reset_email(email)
        if sen_m["status"] == True:
            return SendPasswordResetEmail(
                status=True,
                message="Successfully sent password reset link to {}".format(email),
            )
        else:
            # raise GraphQLError("Email Verification not sent")
            return SendPasswordResetEmail(status=False, message=sen_m["message"])


class ChangePassword(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    class Arguments:
        token = graphene.String(required=True)
        password1 = graphene.String()
        password2 = graphene.String()

    @staticmethod
    def mutate(self, info, token, password1, password2):
        try:
            dt = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            username, validity = dt["user"], dt["validity"]
            if validity:
                if validate_passwords(password1, password2)["status"] == False:
                    return ChangePassword(
                        status=False,
                        message=validate_passwords(password1, password2)["message"],
                    )
                else:
                    user = ExtendUser.objects.get(email=username)
                    user.set_password(password1)
                    user.save()
                    if Notification.objects.filter(user=user).exists():
                        notification = Notification.objects.get(
                            user=user
                        )
                    else:
                        notification = Notification.objects.create(
                            user=user
                        )
                    notification_message = Message.objects.create(
                        notification=notification,
                        message=f"You have successfully changed your password.",
                        subject="Password changed"
                    )
                    notification_info = {"notification":str(notification_message.notification.id),
                    "message":notification_message.message, 
                    "subject":notification_message.subject}
                    push_to_client(user.id, notification_info)
                    email_send = SendEmailNotification(user.email)
                    email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)
                    return ChangePassword(status=True, message="Password Change Successful")
            else:
                return ChangePassword(status=False, message="Invalid Token")
            # return ChangePassword(status=True, message = "Verification Successful")
        except Exception as e:
            return ChangePassword(status=False, message=e)


class StartSelling(graphene.Mutation):
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String(required=True)
        firstname = graphene.String(required=True)
        lastname = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        shop_name = graphene.String(required=True)
        shop_url = graphene.String(required=True)
        shop_address = graphene.String(required=True)
        state = graphene.String(required=True)
        lga = graphene.String(required=True)
        landmark = graphene.String(required=True)
        how_you_heard_about_us = graphene.String(required=True)
        accepted_policy = graphene.Boolean(required=True)

    @staticmethod
    def mutate(
        self,
        info,
        token,
        firstname,
        lastname,
        phone_number,
        shop_name,
        shop_url,
        shop_address,
        state,
        lga,
        landmark,
        how_you_heard_about_us,
        accepted_policy,
    ):
        auth = authenticate_user(token)
        if not auth["status"]:
            return StartSelling(status=auth["status"],message=auth["message"])
        c_user = auth["user"]

        if c_user.is_seller == False:
            if SellerProfile.objects.filter(shop_url=shop_url).exists():
                return StartSelling(status=False, message="Shop url already taken")
            else:
                seller = SellerProfile(
                    user=c_user,
                    firstname=firstname,
                    lastname=lastname,
                    phone_number=phone_number,
                    shop_name=shop_name,
                    shop_url=shop_url,
                    shop_address=shop_address,
                    state=state,
                    lga=lga,
                    landmark=landmark,
                    how_you_heard_about_us=how_you_heard_about_us,
                    accepted_policy=accepted_policy,
                )
                seller.save()
                c_user.is_seller = True
                c_user.save()
                if Notification.objects.filter(user=c_user).exists():
                    notification = Notification.objects.get(
                        user=c_user
                    )
                else:
                    notification = Notification.objects.create(
                        user=c_user
                    )
                notification_message = Message.objects.create(
                    notification=notification,
                    message=f"You have successfully created a seller's account",
                    subject="Seller account"
                )
                notification_info = {"notification":str(notification_message.notification.id),
                "message":notification_message.message, 
                "subject":notification_message.subject}
                push_to_client(c_user.id, notification_info)
                email_send = SendEmailNotification(c_user.email)
                email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)
                return StartSelling(
                    status=True, message="Seller account created successfully"
                )
                # if seller.save():
                #     c_user.is_seller = True
                #     c_user.save()
                #     return StartSelling(status=True, message="Seller account created successfully")
                # return StartSelling(status=False, message="Error Occured, try again later")
        else:
            return StartSelling(status=False, message="User is already a seller")




class AccountNameRetrieval(graphene.Mutation):
    message = graphene.String()
    account_number = graphene.String()
    account_name = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        # token = graphene.String()
        account_number = graphene.String()
        # bank_name = graphene.String()
        bank_code = graphene.String()

    @staticmethod
    def mutate(self, info, account_number, bank_code):
        body, myurl = {
            "account_number": account_number,
            "account_bank": bank_code,
        }, "https://api.flutterwave.com/v3/accounts/resolve"
        response = send_post_request(myurl, body)
        response_status, response_message = response["status"], response["message"]
        account_number, account_name = "null", "null"
        if response_status == "success":
            account_number, account_name = (
                response["data"]["account_number"],
                response["data"]["account_name"],
            )
            return AccountNameRetrieval(
                status=True,
                message="Bank info Retreived",
                account_number=account_number,
                account_name=account_name,
            )
        elif response_status == "error":
            return AccountNameRetrieval(
                status=False,
                message=response_message,
                account_number=account_number,
                account_name=account_name,
            )
        else:
            return AccountNameRetrieval(
                status=False,
                message=response_message,
                account_number=account_number,
                account_name=account_name,
            )


class SellerVerification(graphene.Mutation):
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String(required=True)
        account_number = graphene.String(required=True)
        prefered_id = graphene.String(required=True)
        prefered_id_url = graphene.String(required=True)
        bvn = graphene.String(required=True)
        account_number = graphene.String(required=True)
        account_name = graphene.String(required=True)
        bank_name = graphene.String(required=True)
        bank_sort_code = graphene.String(required=True)
        accepted_vendor_policy = graphene.Boolean(required=True)

    @staticmethod
    def mutate(
        self,
        info,
        token,
        accepted_vendor_policy,
        prefered_id,
        prefered_id_url,
        bvn,
        account_number,
        bank_name,
        bank_sort_code,
        account_name,
    ):
        auth = authenticate_user(token)
        if not auth["status"]:
            return SellerVerification(status=auth["status"],message=auth["message"])
        c_user = auth["user"]
        userid = c_user.id

        seller = {}

        try:
            seller = SellerProfile.objects.get(user=userid)
        except Exception as e:
            return CompleteSellerVerification(status=False, message="you are not yet a seller")

        if seller.seller_is_verified == False:
            if seller.accepted_vendor_policy == False:

                try:
                    (
                        seller.accepted_vendor_policy,
                        seller.prefered_id,
                        seller.prefered_id_url,
                    ) = (accepted_vendor_policy, prefered_id, prefered_id_url)
                    (
                        seller.bvn,
                        seller.bank_name,
                        seller.bank_sort_code,
                        seller.bank_account_number,
                    ) = (bvn, bank_name, bank_sort_code, account_number)
                    seller.bank_account_name = account_name
                    seller.save()
                    return StartSelling(
                        status=True,
                        message="Verification in progress, this might take a few hours",
                    )
                except Exception as e:
                    return StartSelling(status=True, message=e)
            else:
                return StartSelling(
                    status=False, message="Verification is still pending"
                )
        else:
            return StartSelling(status=False, message="Seller is already Verified")


class CompleteSellerVerification(graphene.Mutation):
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        email = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, email):
        try:
            c_user = ExtendUser.objects.get(email=email)
            userid = c_user.id
            print

            seller = {}
            try:
                seller = SellerProfile.objects.get(user=userid)
            except Exception as e:
                return CompleteSellerVerification(status=False, message="user is not a seller")
            
            seller.seller_is_verified = True
            seller.seller_is_rejected = False
            seller.save()
            if seller.seller_is_verified == True:
                store_name = seller.shop_name
                if not StoreDetail.objects.filter(user = c_user).exists():
                    while StoreDetail.objects.filter(store_name = store_name).exists():
                        random_suffix = str(uuid.uuid4())[:8]
                        store_name = f"{store_name} {random_suffix}"

                    StoreDetail.objects.create(
                        user = c_user,
                        store_name = store_name,
                        email=c_user.email,
                        address = seller.shop_address
                    )
                
                if not Wallet.objects.filter(owner = seller.user).exists():
                    Wallet.objects.create(
                        owner = seller.user
                    )
                if Notification.objects.filter(user=c_user).exists():
                    notification = Notification.objects.get(
                        user=c_user
                    )
                else:
                    notification = Notification.objects.create(
                        user=c_user
                    )
                notification_message = Message.objects.create(
                    notification=notification,
                    message=f"your seller verification has been completed",
                    subject="Seller Verification Completed"
                )
                notification_info = {"notification":str(notification_message.notification.id),
                    "message":notification_message.message, 
                    "subject":notification_message.subject}
                push_to_client(c_user.id, notification_info)
                email_send = SendEmailNotification(c_user.email)
                email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)
                return CompleteSellerVerification(status=True, message="Successful")
            else:
                return CompleteSellerVerification(status=False, message="Not Accepted as a Seller")
        except Exception as e:
            return CompleteSellerVerification(status=False, message=e)


class RejectSellerVerification(graphene.Mutation):
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        email = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, email):
        try:
            c_user = ExtendUser.objects.get(email=email)
            userid = c_user.id
            print

            seller = {}
            try:
                seller = SellerProfile.objects.get(user=userid)
            except Exception as e:
                return CompleteSellerVerification(status=False, message="user is not a seller")
            
            seller.seller_is_verified = False
            seller.seller_is_rejected = True
            seller.save()
            
            
            if Notification.objects.filter(user=c_user).exists():
                notification = Notification.objects.get(
                    user=c_user
                )
            else:
                notification = Notification.objects.create(
                    user=c_user
                )
            notification_message = Message.objects.create(
                notification=notification,
                message=f"Seller Verification Failed",
                subject="Failed Verification"
            )
            notification_info = {"notification":str(notification_message.notification.id),
                "message":notification_message.message, 
                "subject":notification_message.subject}
            push_to_client(c_user.id, notification_info)
            email_send = SendEmailNotification(c_user.email)
            email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)
            return CompleteSellerVerification(status=True, message="Successful")
        except Exception as e:
            return CompleteSellerVerification(status=False, message=e)


class UserAccountUpdate(graphene.Mutation):
    message = graphene.String()
    token = graphene.String()
    status = graphene.Boolean() 

    class Arguments:
        token = graphene.String(required=True)
        new_first_name = graphene.String(required=True)
        new_last_name = graphene.String(required=True)
        new_email = graphene.String(required=True)
        new_phone_number = graphene.String(required=True)

    @staticmethod
    def mutate(
        self, info, token, new_first_name, new_last_name, new_email, new_phone_number
    ):
        auth = authenticate_user(token)
        if not auth["status"]:
            return UserAccountUpdate(status=auth["status"],message=auth["message"])
        c_user = auth["user"]
        fullname,email = "{} {}".format(new_first_name, new_last_name), c_user.email

        def u_update(c_email):
            try:
                us = ExtendUser.objects.get(email=c_email)
                us_id = us.id
                us.full_name, us.email, us.username = fullname, new_email, new_email
                us.first_name, us.last_name, us.phone_number = (
                    new_first_name,
                    new_last_name,
                    new_phone_number,
                )
                us.save()

                if us.is_seller == True:
                    se = SellerProfile.objects.get(user=us_id)
                    se.firstname, se.lastname, se.phone_number = (
                        new_first_name,
                        new_last_name,
                        new_phone_number,
                    )
                    se.save()
                    return True
                return True
            except Exception as e:
                return e

        if ExtendUser.objects.filter(email=new_email).exists():
            f_user = ExtendUser.objects.get(email=new_email)
            f_id = f_user.id
            if c_user.id == f_id:
                tu = u_update(email)
                if tu == True:
                    if Notification.objects.filter(user=c_user).exists():
                        notification = Notification.objects.get(
                            user=f_user
                        )
                    else:
                        notification = Notification.objects.create(
                            user=f_user
                        )
                    notification_message = Message.objects.create(
                        notification=notification,
                        message=f"Your account has been updated successfully",
                        subject="Account update"
                    )
                    notification_info = {"notification":str(notification_message.notification.id),
                    "message":notification_message.message, 
                    "subject":notification_message.subject}
                    push_to_client(f_user.id, notification_info)
                    email_send = SendEmailNotification(f_user.email)
                    email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)
                    return UserAccountUpdate(
                        status=True, message="Update Successful", token=token
                    )
                else:
                    return UserAccountUpdate(status=False, message=tu)
            else:
                return UserAccountUpdate(status=False, message="Email already in use")
        else:
            ct = int(("{}".format(time.time())).split(".")[0])
            payload = {"username": new_email, "exp": ct + 151200, "origIat": ct}
            n_token = jwt.encode(
                payload, settings.SECRET_KEY, algorithm="HS256"
            ).decode("utf-8")
            tu = u_update(email)
            if tu == True:
                if Notification.objects.filter(user=c_user).exists():
                    notification = Notification.objects.get(
                        user=c_user
                    )
                else:
                    notification = Notification.objects.create(
                        user=c_user
                    )
                notification_message = Message.objects.create(
                    notification=notification,
                    message=f"Your account has been updated successfully",
                    subject="Account update"
                )
                notification_info = {"notification":str(notification_message.notification.id),
                "message":notification_message.message, 
                "subject":notification_message.subject}
                push_to_client(c_user.id, notification_info)
                email_send = SendEmailNotification(c_user.email)
                email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)
                return UserAccountUpdate(
                    status=True, message="Update Successful", token=n_token
                )
            else:
                return UserAccountUpdate(status=False, message=tu)


class UserPasswordUpdate(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    class Arguments:
        token = graphene.String(required=True)
        current_password = graphene.String()
        new_password = graphene.String()

    @staticmethod
    def mutate(self, info, token, current_password, new_password):
        try:
            email = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])[
                "username"
            ]
            c_user = ExtendUser.objects.get(email=email)
            hashed_password = c_user.password
            vup = validate_user_passwords(new_password)
            if vup:
                check_password
                matchcheck = check_password(current_password, hashed_password)
                # user_t = auth.authenticate(username=email,password=current_password)
                # if user_t is not None:
                if matchcheck:
                    c_user.set_password(new_password)
                    c_user.save()
                    if Notification.objects.filter(user=c_user).exists():
                        notification = Notification.objects.get(
                            user=c_user
                        )
                    else:
                        notification = Notification.objects.create(
                            user=c_user
                        )
                    notification_message = Message.objects.create(
                        notification=notification,
                        message=f"Your password was reset successfully",
                        subject="Password reset"
                    )
                    notification_info = {"notification":str(notification_message.notification.id), "message":notification_message.message, "subject":notification_message.subject}
                    push_to_client(c_user.id, notification_info)
                    email_send = SendEmailNotification(c_user.email)
                    email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)
                    return UserPasswordUpdate(
                        status=True, message="Password Change Successful"
                    )
                else:
                    return UserPasswordUpdate(
                        status=False, message="Current Password is incorrect"
                    )
            else:
                return UserPasswordUpdate(status=False, message=vup["message"])
        except Exception as e:
            return UserPasswordUpdate(status=False, message=e)


class StoreUpdate(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    class Arguments:
        token = graphene.String(required=True)
        store_banner = graphene.String(required=True)
        store_description = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, token, store_banner, store_description):
        auth = authenticate_user(token)
        if not auth["status"]:
            return StoreUpdate(status=auth["status"],message=auth["message"])
        c_user = auth["user"]
        try:
            seller = SellerProfile.objects.get(user=c_user.id)
            seller.store_banner_url, seller.store_description = (
                store_banner,
                store_description,
            )
            seller.save()
            if Notification.objects.filter(user=c_user).exists():
                notification = Notification.objects.get(
                    user=c_user
                )
            else:
                notification = Notification.objects.create(
                    user=c_user
                )
            notification_message = Message.objects.create(
                notification=notification,
                message=f"Your store info has been updated successfully",
                subject="Store Update"
            )
            notification_info = {"notification":str(notification_message.notification.id),
                "message":notification_message.message, 
                "subject":notification_message.subject}
            push_to_client(c_user.id, notification_info)
            email_send = SendEmailNotification(c_user.email)
            email_send.send_only_one_paragraph(notification_message.subject, notification_message.message)
            return StoreUpdate(status=True, message="Update Successful")
        except Exception as e:
            return StoreUpdate(status=False, message=e)


class StoreLocationUpdate(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()
    class Arguments:
        token = graphene.String(required=True)
        shop_address = graphene.String(required=True)
        state = graphene.String(required=True)
        city = graphene.String(required=True)
        lga = graphene.String(required=True)
        landmark = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, token, shop_address, state, city, lga, landmark):
        auth = authenticate_user(token)
        if not auth["status"]:
            return StoreLocationUpdate(status=auth["status"],message=auth["message"])
        c_user = auth["user"]
        try:
            seller = SellerProfile.objects.get(user=c_user.id)
            seller.shop_address, seller.state, seller.city = shop_address, state, city
            seller.lga, seller.landmark = lga, landmark
            seller.save()
            return StoreLocationUpdate(status=True, message="Update Successful")
        except Exception as e:
            return StoreLocationUpdate(status=False, message=e)

class StoreBanner(graphene.Mutation):
    status = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        token = graphene.String(required=True)
        image_url = graphene.String(required=True)
        store_description = graphene.String()

    @staticmethod
    def mutate(self, info, token, image_url, store_description=None):
        auth = authenticate_user(token)
        if not auth["status"]:
            return StoreBanner(status=auth["status"],message=auth["message"])
        user = auth["user"]
        if user.is_seller:
            seller = SellerProfile.objects.filter(user=user)
            if store_description:
                seller.update(store_banner_url=image_url, store_description=store_description)
                return StoreBanner(
                    status=True,
                    message="Banner and Description added Successfully"
                )
            else:
                seller.update(store_banner_url=image_url)
                return StoreBanner(
                    status=True,
                    message="Banner added Successfully"
                )
            
        else:
            return StoreBanner(status=False,message="User is not a seller")

class FlagVendor(graphene.Mutation):
    message = graphene.String()
    status = graphene.Boolean()
    
    class Arguments:
        token=graphene.String(required=True)
        id=graphene.String(required=True)
        red_flagged_vendor = graphene.Boolean(required=True)
    
    @staticmethod
    def mutate(self, info, token, id, red_flagged_vendor):
        auth = authenticate_admin(token)
        if not auth["status"]:
          return FlagVendor(status=auth["status"], message=auth["message"])
        user = auth["user"]
        if user:
            vendor = ExtendUser.objects.get(id=id)
            vendor.is_flagged= red_flagged_vendor
            vendor.save()
            return FlagVendor(status=True, message="Successfully changed vendor status")
        return FlagVendor(status=False, message="Wrong token provided")

class SendEmailToUsers(graphene.Mutation):
    message = graphene.String()
    status = graphene.Boolean()
    
    class Arguments:
        token=graphene.String(required=True)
        user_list = graphene.List(graphene.String, required=True)
        template = graphene.String(required=True)
        subject = graphene.String(required=True)
    
    @staticmethod
    def mutate(self, info, token, user_list: List[str], template:str, subject:str):
        auth = authenticate_admin(token)
        if not auth["status"]:
          return SendEmailToUsers(status=auth["status"], message=auth["message"])
        user = auth["user"]
        if user:
            html_template = Template(template)
            userEmailToContent: Dict[str, Dict[str, str]] = {}
            usersMap = ExtendUser.get_users_dict_by_ids(user_list)

            for id in user_list:
                if usersMap[id]:
                    user_context = {'user': user}
                    email = usersMap[id].email
                    html_string = html_template.render(Context(user_context))
                    emailContent: Dict[str, str] = {
                        "template": html_string,
                        "subject" : subject
                    }
                    userEmailToContent[email] = emailContent

            send_emails_in_batches(userEmailToContent, 5, 1)       
        return SendEmailToUsers(status=False, message="Wrong token provided")

def send_emails_in_batches(userEmailToTemplate: Dict[str, Dict[str, str]], batch_size, delay):
    actions = list(userEmailToTemplate.items())  # Convert dictionary to a list of tuples

    for i in range(0, len(actions), batch_size):
        batch = actions[i:i+batch_size]
        print("batch", batch)
        for email, content in batch:
            send_generic_email_through_PHP([email], content["template"], content["subject"]) 
        if i + batch_size < len(actions):
            time.sleep(delay)
       
