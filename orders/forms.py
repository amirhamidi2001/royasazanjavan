from django import forms
from django.core.exceptions import ValidationError
from .models import Order, Coupon


class OrderCreateForm(forms.ModelForm):
    """Form for creating an order at checkout."""

    # Additional fields not in model
    terms = forms.BooleanField(
        required=True, error_messages={"required": "شما باید شرایط و قوانین را بپذیرید"}
    )

    coupon_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "کد تخفیف"}
        ),
    )

    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "apartment",
            "city",
            "state",
            "zip_code",
            "country",
            "notes",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام خانوادگی"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "ایمیل"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "شماره تلفن"}
            ),
            "address": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "آدرس کامل"}
            ),
            "apartment": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "واحد، پلاک (اختیاری)"}
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "شهر"}
            ),
            "state": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "استان"}
            ),
            "zip_code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "کد پستی"}
            ),
            "country": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "یادداشت (اختیاری)",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    #     # Pre-fill user information if user is authenticated
    #     if self.user and self.user.is_authenticated:
    #         self.fields["first_name"].initial = self.user.first_name
    #         self.fields["last_name"].initial = self.user.last_name
    #         self.fields["email"].initial = self.user.email

    def clean_email(self):
        """Validate email format."""
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower().strip()
        return email

    def clean_phone(self):
        """Validate phone number."""
        phone = self.cleaned_data.get("phone")
        # Remove common separators
        phone = (
            phone.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        )

        if not phone.isdigit():
            raise ValidationError("شماره تلفن باید فقط شامل اعداد باشد")

        if len(phone) < 10:
            raise ValidationError("شماره تلفن باید حداقل ۱۰ رقم باشد")

        return phone

    def clean_zip_code(self):
        """Validate zip code."""
        zip_code = self.cleaned_data.get("zip_code")
        if zip_code:
            zip_code = zip_code.replace("-", "").replace(" ", "")
            if not zip_code.isdigit():
                raise ValidationError("کد پستی باید فقط شامل اعداد باشد")
        return zip_code


class CouponApplyForm(forms.Form):
    """Form for applying a coupon code."""

    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "کد تخفیف را وارد کنید"}
        ),
    )

    def __init__(self, *args, **kwargs):
        self.total_amount = kwargs.pop("total_amount", 0)
        super().__init__(*args, **kwargs)

    def clean_code(self):
        """Validate coupon code."""
        code = self.cleaned_data.get("code")

        if not code:
            raise ValidationError("لطفاً کد تخفیف را وارد کنید")

        code = code.upper().strip()

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise ValidationError("کد تخفیف نامعتبر است")

        if not coupon.is_valid():
            raise ValidationError("کد تخفیف منقضی شده یا غیرفعال است")

        if not coupon.can_use(self.total_amount):
            raise ValidationError(
                f"حداقل مبلغ خرید برای استفاده از این کد تخفیف {coupon.min_purchase_amount:,} تومان است"
            )

        self.coupon = coupon
        return code

    def get_discount_amount(self):
        """Get calculated discount amount."""
        if hasattr(self, "coupon"):
            return self.coupon.calculate_discount(self.total_amount)
        return 0
