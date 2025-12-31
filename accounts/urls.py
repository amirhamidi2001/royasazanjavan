from django.urls import path, include
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    EmailVerificationView,
    ResendVerificationEmailView,
    ForgotPasswordView,
    ResetPasswordView,
    ChangePasswordView,
)

app_name = "accounts"

urlpatterns = [
    # Authentication
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    # Email Verification
    path(
        "verify-email/<uidb64>/<token>/",
        EmailVerificationView.as_view(),
        name="verify-email",
    ),
    path(
        "resend-verification/",
        ResendVerificationEmailView.as_view(),
        name="resend-verification",
    ),
    # Password Reset
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path(
        "reset-password/<uidb64>/<token>/",
        ResetPasswordView.as_view(),
        name="reset-password",
    ),
    # Change Password
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    # Google OAuth (allauth)
    # path("", include("allauth.urls")),
]
