from django.core.exceptions import ValidationError
import re


def validate_iranian_cellphone_number(value):
    """
    Enter a valid Iranian cellphone number.
    """
    pattern = r"^09\d{9}$"
    if not re.match(pattern, value):
        raise ValidationError(
            "یک شماره تلفن همراه معتبر ایرانی وارد کنید. (09123456789)"
        )
