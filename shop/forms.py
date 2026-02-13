from django import forms
from .models import Product


class ProductFilterForm(forms.Form):
    """
    Form for filtering products by various criteria
    """

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "جستجوی محصول...",
                "dir": "rtl",
            }
        ),
    )

    category = forms.CharField(required=False, widget=forms.HiddenInput())

    type = forms.ChoiceField(
        choices=[("", "همه نوع‌ها")] + list(Product.PRODUCT_TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={"class": "form-select", "dir": "rtl"}),
    )

    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "حداقل قیمت", "dir": "rtl"}
        ),
    )

    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "حداکثر قیمت", "dir": "rtl"}
        ),
    )

    is_free = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="فقط محصولات رایگان",
    )

    sort = forms.ChoiceField(
        choices=[
            ("-created_at", "جدیدترین"),
            ("created_at", "قدیمی‌ترین"),
            ("price", "ارزان‌ترین"),
            ("-price", "گران‌ترین"),
            ("title", "الفبایی (الف-ی)"),
            ("-title", "الفبایی (ی-الف)"),
        ],
        required=False,
        initial="-created_at",
        widget=forms.Select(attrs={"class": "form-select", "dir": "rtl"}),
    )


class ProductSearchForm(forms.Form):
    """
    Simple search form for quick product search
    """

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "جستجو در محصولات...",
                "dir": "rtl",
                "autocomplete": "off",
            }
        ),
    )
