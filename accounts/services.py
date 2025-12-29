from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

from .tokens import email_verification_token


class EmailService:
    """
    Service class responsible for sending emails.
    """

    @staticmethod
    def send_verification_email(user, request):
        """
        Send account verification email to the user.
        """
        token = email_verification_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        verification_url = request.build_absolute_uri(
            f"/accounts/verify-email/{uid}/{token}/"
        )

        context = {
            "user": user,
            "verification_url": verification_url,
        }

        html_message = render_to_string(
            "accounts/emails/activation_email.html",
            context,
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject="تأیید حساب کاربری",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

    @staticmethod
    def send_password_reset_email(user, request):
        """
        Send password reset email to the user.
        """
        token = email_verification_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = request.build_absolute_uri(
            f"/accounts/reset-password/{uid}/{token}/"
        )

        context = {
            "user": user,
            "reset_url": reset_url,
        }

        html_message = render_to_string(
            "accounts/emails/reset_password_email.html",
            context,
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject="بازیابی رمز عبور",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
