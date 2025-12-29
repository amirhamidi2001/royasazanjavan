from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """
    Form for registering a new user using email and password.
    """

    email = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "ایمیل خود را وارد کنید"}
        ),
    )
    password1 = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "رمز عبور"}
        ),
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "تکرار رمز عبور"}
        ),
    )

    class Meta:
        model = User
        fields = ("email",)

    def clean_email(self):
        """
        Validate that the email is unique.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email

    def clean_password2(self):
        """
        Validate password confirmation and password strength.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("رمزهای عبور باهم مطابقت ندارند.")

        if len(password2) < 8:
            raise ValidationError(
                "این رمز عبور خیلی کوتاه است. باید حداقل ۸ کاراکتر داشته باشد."
            )

        try:
            validate_password(password2)
        except ValidationError:
            raise ValidationError(
                "این رمز عبور خیلی ساده است، لطفا رمز پیچیده‌تری انتخاب کنید."
            )

        return password2


class UserLoginForm(AuthenticationForm):
    """
    Login form that authenticates users using email and password.
    """

    username = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "ایمیل"}
        ),
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "رمز عبور"}
        ),
    )

    error_messages = {
        "invalid_login": "ایمیل یا رمز عبور اشتباه است.",
        "inactive": "این حساب کاربری غیرفعال است.",
    }


class ForgotPasswordForm(forms.Form):
    """
    Form for requesting a password reset via email.
    """

    email = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "ایمیل خود را وارد کنید"}
        ),
    )


class ResetPasswordForm(forms.Form):
    """
    Form for resetting the user's password.
    """

    password1 = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "رمز عبور جدید"}
        ),
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "تکرار رمز عبور جدید"}
        ),
    )

    def clean_password2(self):
        """
        Validate that the new passwords match.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("رمزهای عبور مطابقت ندارند.")

        return password2


class ChangePasswordForm(forms.Form):
    """
    Form for changing the user's password.
    """

    old_password = forms.CharField(
        label="رمز عبور فعلی",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "رمز عبور فعلی"}
        ),
    )
    new_password1 = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "رمز عبور جدید"}
        ),
    )
    new_password2 = forms.CharField(
        label="تکرار رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "تکرار رمز عبور جدید"}
        ),
    )

    def __init__(self, user, *args, **kwargs):
        """
        Initialize the form with the current user.
        """
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        """
        Validate the user's current password.
        """
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise ValidationError("رمز عبور فعلی اشتباه است.")
        return old_password

    def clean_new_password2(self):
        """
        Validate that the new passwords match.
        """
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("رمزهای عبور جدید مطابقت ندارند.")

        return password2
