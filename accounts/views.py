from django.shortcuts import render, redirect
from django.contrib.auth import (
    login,
    logout,
    authenticate,
    get_user_model,
    update_session_auth_hash,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, FormView, View
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ChangePasswordForm,
)
from .tokens import email_verification_token
from .services import EmailService

User = get_user_model()


class UserRegistrationView(CreateView):
    """
    View for registering a new user.
    """

    form_class = UserRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    @method_decorator(ratelimit(key="ip", rate="5/h", method="POST"))
    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to the home page
        if request.user.is_authenticated:
            return redirect("website:index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Save user with is_verified set to False
        user = form.save(commit=False)
        user.is_verified = False
        user.save()

        # Send verification email
        try:
            EmailService.send_verification_email(user, self.request)
            messages.success(
                self.request,
                "ثبت‌نام با موفقیت انجام شد. لطفاً ایمیل خود را بررسی و حساب خود را فعال کنید.",
            )
        except Exception:
            messages.warning(
                self.request,
                "حساب شما ایجاد شد اما ارسال ایمیل با مشکل مواجه شد. لطفاً با پشتیبانی تماس بگیرید.",
            )

        return redirect(self.success_url)

    def form_invalid(self, form):
        # Display form validation errors
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)


class EmailVerificationView(View):
    """
    View for verifying the user's email address.
    """

    def get(self, request, uidb64, token):
        try:
            # Decode the user ID from the URL
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Validate the verification token
        if user is not None and email_verification_token.check_token(user, token):
            # Check if the account is already verified
            if user.is_verified:
                messages.info(request, "حساب شما قبلاً فعال شده است.")
                return redirect("accounts:login")

            # Activate the user account
            user.is_verified = True
            user.save()

            messages.success(
                request,
                "حساب شما با موفقیت فعال شد. اکنون می‌توانید وارد شوید.",
            )
            return redirect("accounts:login")

        messages.error(request, "لینک فعال‌سازی نامعتبر یا منقضی شده است.")
        return redirect("accounts:resend-verification")


class ResendVerificationEmailView(FormView):
    """
    View for resending the email verification link.
    """

    template_name = "accounts/resend_verification.html"
    form_class = ForgotPasswordForm  # Reusing the same form
    success_url = reverse_lazy("accounts:login")

    @method_decorator(ratelimit(key="ip", rate="3/h", method="POST"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data["email"]

        try:
            user = User.objects.get(email=email)

            # Check if the account is already verified
            if user.is_verified:
                messages.info(self.request, "حساب شما قبلاً فعال شده است.")
                return redirect("accounts:login")

            # Resend verification email
            EmailService.send_verification_email(user, self.request)
            messages.success(
                self.request,
                "ایمیل فعال‌سازی مجدداً ارسال شد. لطفاً ایمیل خود را بررسی کنید.",
            )
        except User.DoesNotExist:
            # Prevent user enumeration
            messages.success(
                self.request,
                "اگر این ایمیل در سیستم وجود داشته باشد، ایمیل فعال‌سازی برای شما ارسال خواهد شد.",
            )

        return redirect(self.success_url)


class UserLoginView(LoginView):
    """
    User login view.
    """

    form_class = UserLoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    @method_decorator(ratelimit(key="ip", rate="10/h", method="POST"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()

        # Check if the user is verified
        if not user.is_verified:
            messages.error(
                self.request,
                "لطفاً ابتدا ایمیل خود را تأیید کنید. ایمیل فعال‌سازی برای شما ارسال شده است.",
            )
            return redirect("accounts:resend-verification")

        # Check if the user account is active
        if not user.is_active:
            messages.error(
                self.request,
                "حساب کاربری شما غیرفعال شده است. لطفاً با پشتیبانی تماس بگیرید.",
            )
            return redirect("accounts:login")

        login(self.request, user)
        messages.success(self.request, "خوش آمدید!")

        # Redirect to next URL or home page
        next_url = self.request.GET.get("next", "website:index")
        return redirect(next_url)

    def form_invalid(self, form):
        messages.error(self.request, "ایمیل یا رمز عبور اشتباه است.")
        return super().form_invalid(form)


class UserLogoutView(LoginRequiredMixin, LogoutView):
    """
    User logout view.
    """

    next_page = "accounts:login"

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "با موفقیت خارج شدید.")
        return super().dispatch(request, *args, **kwargs)


class ForgotPasswordView(FormView):
    """
    View for requesting a password reset.
    """

    form_class = ForgotPasswordForm
    template_name = "accounts/forgot_password.html"
    success_url = reverse_lazy("accounts:login")

    @method_decorator(ratelimit(key="ip", rate="5/h", method="POST"))
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("website:index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data["email"]

        try:
            user = User.objects.get(email=email, is_active=True)
            EmailService.send_password_reset_email(user, self.request)
        except User.DoesNotExist:
            pass  # Prevent user enumeration

        # Same message for all cases
        messages.success(
            self.request,
            "اگر این ایمیل در سیستم وجود داشته باشد، لینک بازیابی رمز عبور برای شما ارسال خواهد شد.",
        )

        return redirect(self.success_url)


class ResetPasswordView(FormView):
    """
    View for resetting the user's password.
    """

    form_class = ResetPasswordForm
    template_name = "accounts/reset_password.html"
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        # Extract uid and token from the URL
        self.uidb64 = kwargs.get("uidb64")
        self.token = kwargs.get("token")

        # Initial validation of user and token
        try:
            uid = force_str(urlsafe_base64_decode(self.uidb64))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            self.user = None

        # Validate the reset token
        if self.user is None or not email_verification_token.check_token(
            self.user,
            self.token,
        ):
            messages.error(request, "لینک بازیابی نامعتبر یا منقضی شده است.")
            return redirect("accounts:forgot-password")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Set the new password
        new_password = form.cleaned_data["password1"]
        self.user.set_password(new_password)
        self.user.save()

        messages.success(
            self.request,
            "رمز عبور شما با موفقیت تغییر کرد. اکنون می‌توانید با رمز جدید وارد شوید.",
        )

        return redirect(self.success_url)


class ChangePasswordView(LoginRequiredMixin, FormView):
    """
    View for changing the password of a logged-in user.
    """

    form_class = ChangePasswordForm
    template_name = "accounts/change_password.html"
    success_url = reverse_lazy("website:index")

    def get_form_kwargs(self):
        # Pass the current user to the form
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        new_password = form.cleaned_data["new_password1"]
        user = self.request.user
        user.set_password(new_password)
        user.save()

        # Update the session to prevent logout
        update_session_auth_hash(self.request, user)

        messages.success(self.request, "رمز عبور شما با موفقیت تغییر کرد.")

        return redirect(self.success_url)

    def form_invalid(self, form):
        # Display form validation errors
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)
