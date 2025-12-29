from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailVerifiedBackend(ModelBackend):
    """
    Custom authentication backend that only authenticates
    users who are verified.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user using email and password,
        ensuring the user is active and verified.
        """
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        # Check password validity
        if not user.check_password(password):
            return None

        # Check if user account is active
        if not user.is_active:
            return None

        # Check if user is verified (important)
        if not user.is_verified:
            return None

        return user
