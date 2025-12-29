from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for handling Google OAuth authentication.
    """

    def pre_social_login(self, request, sociallogin):
        """
        If a user with the same Google email already exists,
        connect the social account to the existing user.
        """
        if sociallogin.is_existing:
            return

        # Retrieve email from Google account data
        email = sociallogin.account.extra_data.get("email")
        if not email:
            return

        # Check if a user with this email already exists
        try:
            user = User.objects.get(email=email)
            # Connect Google account to the existing user
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        """
        Save a new user authenticated via Google.
        """
        user = super().save_user(request, sociallogin, form)

        # Google users are already verified
        user.is_verified = True
        user.save()

        # Update user profile if necessary
        extra_data = sociallogin.account.extra_data
        profile = user.user_profile

        if not profile.first_name:
            profile.first_name = extra_data.get("given_name", "")

        if not profile.last_name:
            profile.last_name = extra_data.get("family_name", "")

        profile.save()

        return user
