import graphene
import jwt
from graphene_django import DjangoObjectType
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations
from django.conf import settings
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from .validate import validate_email, validate_passwords
from .sendmail import send_confirmation_email, user_loggedIN, expire_token, send_password_reset_email
from .models import ExtendUser
from graphql_jwt.utils import jwt_encode, jwt_payload
from django.contrib.auth import authenticate
from graphql_jwt.shortcuts import create_refresh_token, get_token
import time
import datetime;
# import cookbook.ingredients.schema

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)
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
        user = get_user_model()(
            username=email,
            email=email,
            full_name=full_name,
        )


        if validate_email(email)['status'] == False:
            return CreateUser(status=False, message = validate_email(email)['message'])
        elif validate_passwords(password1, password2)['status'] == False:
            return CreateUser(status=False, message = validate_passwords(password1, password2)['message'])
        else:
            sen_m = send_confirmation_email(email)
            if sen_m['status'] == True:
                user.set_password(password1)
                user.save()
                return CreateUser(status=True, email_text=sen_m['email'], message="Successfully created account for, {}".format(user.username))
            else:
                # raise GraphQLError("Email Verification not sent") 
                return CreateUser(status=False, message = sen_m['message']) 
        # raise Exception('Invalid Link!')

class ResendVerification(graphene.Mutation):
    user = graphene.Field(UserType)
    sender = settings.EMAIL_HOST_USER
    status = graphene.Boolean()
    message = graphene.String()
    email_text = graphene.String()
    class Arguments:
        email = graphene.String(required=True)
    
    @staticmethod
    def mutate(self, info, email):
        sen_m = send_confirmation_email(email)
        if sen_m['status'] == True:
            return ResendVerification(status=True, email_text=sen_m['email'], message="Successfully sent email to {}".format(email))
        else:
            # raise GraphQLError("Email Verification not sent") 
            return ResendVerification(status=False, message = sen_m['message']) 

class VerifyUser(graphene.Mutation):
    user = graphene.Field(UserType)
    status = graphene.Boolean()
    message = graphene.String()
    class Arguments:
        token = graphene.String(required=True)
    
    @staticmethod
    def mutate(self, info, token):
        username = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])["user"]
        try:
            user = ExtendUser.objects.get(email=username)
            user.is_verified = True
            user.save()
            return CreateUser(status=True, message = "Verification Successful")
        except Exception as e:
            return CreateUser(status=False, message = e)

class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    message = graphene.String()
    token = graphene.String()
    refresh_token = graphene.String()
    payload_string = graphene.String()
    status = graphene.Boolean()
    verification_prompt = graphene.String()
    payload = graphene.String()
    time_diff = graphene.String()

    class Arguments:
        email = graphene.String()
        password = graphene.String()
    
    @staticmethod
    def mutate(self, info, email, password):
        user = authenticate(username=email, password=password)
        error_message = 'Invalid login credentials'
        success_message = "You logged in successfully."
        verification_error = 'Your email is not verified'

        if user:
            if user.is_verified:

                ct = int(('{}'.format(time.time())).split('.')[0])
                payload = {
                    user.USERNAME_FIELD: email,
                    'exp': ct + 151200,
                    'origIat': ct
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
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
                # token = get_token(user)
                refresh_token = create_refresh_token(user)
                return LoginUser(user=user, status=True, token=token, message=success_message, payload=payload)
            return LoginUser(status=False, message=verification_error)
        return LoginUser(status=False, message=error_message)

class VerifyToken(graphene.Mutation):
    user = graphene.Field(UserType)
    message = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String()

    @staticmethod
    def mutate(self, info, token):

        if user_loggedIN(token):
            return VerifyToken(status=True, message="User is Logged in")
        else:
            return VerifyToken(status=False, message="User is not Authenticated")

class RevokeToken(graphene.Mutation):
    user = graphene.Field(UserType)
    message = graphene.String()
    token = graphene.String()
    payload = graphene.String()
    status = graphene.Boolean()

    class Arguments:
        token = graphene.String()

    @staticmethod
    def mutate(self, info, token):
        result = expire_token(token)
        if result['status']:
            return RevokeToken(status=True, message=result['message'], token = result['token'], payload = result['payload'])
        else:
            return RevokeToken(status=True, message=result['message'], token = result['token'])


class SendPasswordResetEmail(graphene.Mutation):
    user = graphene.Field(UserType)
    sender = settings.EMAIL_HOST_USER
    status = graphene.Boolean()
    message = graphene.String()
    email_text = graphene.String()
    class Arguments:
        email = graphene.String(required=True)
    
    @staticmethod
    def mutate(self, info, email):
        sen_m = send_password_reset_email(email)
        if sen_m['status'] == True:
            return SendPasswordResetEmail(status=True, email_text=sen_m['email'], message="Successfully sent password reset link to {}".format(email))
        else:
            # raise GraphQLError("Email Verification not sent") 
            return SendPasswordResetEmail(status=False, message = sen_m['message']) 

class ChangePassword(graphene.Mutation):
    user = graphene.Field(UserType)
    status = graphene.Boolean()
    message = graphene.String()
    class Arguments:
        token = graphene.String(required=True)
        password1 = graphene.String()
        password2 = graphene.String()

    
    @staticmethod
    def mutate(self, info, token, password1, password2):
        try:
            dt = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            username, validity = dt["user"], dt["validity"]
            if validity:
                if validate_passwords(password1, password2)['status'] == False:
                    return CreateUser(status=False, message = validate_passwords(password1, password2)['message'])
                else:
                    user = ExtendUser.objects.get(email=username)
                    user.set_password(password1)
                    user.save()
                    return CreateUser(status=True, message = "Password Change Successful")
            else:
                return ChangePassword(status=False, message = "Invalid Token")
            # return ChangePassword(status=True, message = "Verification Successful")
        except Exception as e:
            return ChangePassword(status=False, message = e)


class AuthMutation(graphene.ObjectType):
    pass



class Mutation(AuthMutation, graphene.ObjectType):
    create_user = CreateUser.Field()
    resend_verification = ResendVerification.Field()
    verify_user = VerifyUser.Field()
    login_user = LoginUser.Field()
    verify_token = VerifyToken.Field()
    revoke_token = RevokeToken.Field()
    send_password_reset_email = SendPasswordResetEmail.Field()
    change_password = ChangePassword.Field()




class Query(UserQuery, MeQuery, graphene.ObjectType):
    pass



schema = graphene.Schema(query=Query, mutation=Mutation)