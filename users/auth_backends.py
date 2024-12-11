from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailOrUsernameAuthBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using either their email or username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        # Try to fetch the user by email or username
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None

        # Verify the password
        if user.check_password(password):
            return user
        return None
