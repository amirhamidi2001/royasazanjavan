from django.contrib.auth import get_user_model

User = get_user_model()


def associate_by_email(backend, details, user=None, *args, **kwargs):
    """
    Associate a social-auth login with an existing user account
    based on email address.
    """

    if user:
        return None

    # Extract email from provider details
    email = details.get("email")
    if email:
        try:
            # Attempt to find an existing user with the same email
            existing_user = User.objects.get(email=email)
            return {"user": existing_user, "is_new": False}
        except User.DoesNotExist:
            # No user found with this email; continue pipeline
            pass

    return None


def mark_email_verified(backend, details, user=None, *args, **kwargs):
    """
    Mark a user's email as verified after successful social authentication.
    """

    if user and not user.is_verified:
        user.is_verified = True
        user.save(update_fields=["is_verified"])

    return None


def update_user_profile(backend, details, user=None, *args, **kwargs):
    """
    Update the user's profile information using data from the
    social authentication provider.
    """

    if not user:
        return None

    # Access related user profile
    profile = user.user_profile

    # Populate first name if missing
    if not profile.first_name and details.get("first_name"):
        profile.first_name = details.get("first_name", "")

    # Populate last name if missing
    if not profile.last_name and details.get("last_name"):
        profile.last_name = details.get("last_name", "")

    # Save profile updates
    profile.save()

    return None
