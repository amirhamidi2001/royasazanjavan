from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from accounts.models import Profile

User = get_user_model()


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information."""

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "phone_number",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام خانوادگی"}
            ),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "09123456789"}
            ),
        }

    def clean_phone_number(self):
        """Validate phone number."""
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number:
            # Remove spaces and dashes
            phone_number = phone_number.replace(" ", "").replace("-", "")

            # Check if it's a valid Iranian mobile number
            if not phone_number.startswith("09") or len(phone_number) != 11:
                raise ValidationError("شماره موبایل باید با 09 شروع شود و 11 رقم باشد")

        return phone_number


class EmailUpdateForm(forms.ModelForm):
    """Form for updating user email."""

    class Meta:
        model = User
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "example@email.com"}
            )
        }

    def clean_email(self):
        """Validate email is unique."""
        email = self.cleaned_data.get("email")

        # Check if email is already taken by another user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("این ایمیل قبلاً استفاده شده است")

        return email.lower()


class PasswordChangeForm(forms.Form):
    """Form for changing password."""

    current_password = forms.CharField(
        label="رمز عبور فعلی",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "رمز عبور فعلی"}
        ),
    )
    new_password = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "رمز عبور جدید"}
        ),
        min_length=8,
    )
    confirm_password = forms.CharField(
        label="تکرار رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "تکرار رمز عبور جدید"}
        ),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        """Verify current password is correct."""
        current_password = self.cleaned_data.get("current_password")

        if not self.user.check_password(current_password):
            raise ValidationError("رمز عبور فعلی صحیح نیست")

        return current_password

    def clean(self):
        """Verify passwords match."""
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError(
                    {"confirm_password": "رمز عبور جدید و تکرار آن مطابقت ندارند"}
                )

        return cleaned_data

    def save(self):
        """Save new password."""
        self.user.set_password(self.cleaned_data["new_password"])
        self.user.save()
        return self.user
