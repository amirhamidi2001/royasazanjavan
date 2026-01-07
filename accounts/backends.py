from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailVerifiedBackend(ModelBackend):
    """
    Custom Django authentication backend that authenticates users
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user using email and password.
        """
        try:
            # Attempt to find a user with the given email
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # No user found with this email
            return None

        # Verify the provided password
        if user.check_password(password):

            # Reject login if the account is disabled
            if not user.is_active:
                return None

            # Reject login if the email is not verified
            if not user.is_verified:
                return None

            # Authentication successful
            return user

        # Password did not match
        return None

    def get_user(self, user_id):
        """
        Retrieve a user instance by primary key.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
