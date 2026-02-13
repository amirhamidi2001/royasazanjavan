# cart/utils.py - توابع کمکی برای سبد خرید

from django.contrib.contenttypes.models import ContentType
from courses.models import Course
from shop.models import Product


def get_product_model_by_type(product_type):
    """
    دریافت مدل محصول بر اساس نوع

    Args:
        product_type (str): نوع محصول ('course' یا 'product')

    Returns:
        Model class or None
    """
    models_map = {
        "course": Course,
        "product": Product,
    }
    return models_map.get(product_type)


def get_product_by_type_and_id(product_type, product_id):
    """
    دریافت شیء محصول بر اساس نوع و ID

    Args:
        product_type (str): نوع محصول
        product_id (int): شناسه محصول

    Returns:
        Product object or None
    """
    model = get_product_model_by_type(product_type)
    if not model:
        return None

    try:
        return model.objects.get(id=product_id, is_active=True)
    except model.DoesNotExist:
        return None


def get_content_type_for_product(product_type):
    """
    دریافت ContentType برای نوع محصول

    Args:
        product_type (str): نوع محصول

    Returns:
        ContentType object or None
    """
    model = get_product_model_by_type(product_type)
    if not model:
        return None

    return ContentType.objects.get_for_model(model)


def calculate_item_price(product_obj, product_type):
    """
    محاسبه قیمت نهایی آیتم بر اساس نوع محصول

    Args:
        product_obj: شیء محصول
        product_type (str): نوع محصول

    Returns:
        Decimal: قیمت نهایی
    """
    if product_type == "course":
        # برای دوره‌ها: قیمت ثابت
        return product_obj.price
    elif product_type == "product":
        # برای محصولات: قیمت با احتساب تخفیف
        return product_obj.get_final_price()
    else:
        return 0


def format_price(price):
    """
    فرمت‌دهی قیمت به صورت خوانا

    Args:
        price: قیمت (Decimal یا int)

    Returns:
        str: قیمت فرمت شده (مثال: "1,500,000 تومان")
    """
    try:
        return f"{int(price):,} تومان"
    except (ValueError, TypeError):
        return "0 تومان"


def get_cart_context_processor(request):
    """
    Context Processor برای نمایش اطلاعات سبد در تمام صفحات

    استفاده:
    در settings.py:
    TEMPLATES = [{
        'OPTIONS': {
            'context_processors': [
                ...
                'cart.utils.get_cart_context_processor',
            ],
        },
    }]
    """
    from cart.cart import CartSession

    cart = CartSession(request.session)
    return {
        "cart_quantity": cart.get_total_quantity(),
        "cart_total": cart.get_total_payment_amount(),
    }


def validate_product_stock(product_obj, product_type, quantity=1):
    """
    بررسی موجودی محصول (فقط برای محصولات فیزیکی)

    Args:
        product_obj: شیء محصول
        product_type (str): نوع محصول
        quantity (int): تعداد درخواستی

    Returns:
        tuple: (is_valid, error_message)
    """
    # دوره‌ها موجودی ندارند
    if product_type == "course":
        return (True, None)

    # بررسی موجودی محصولات
    if product_type == "product":
        if hasattr(product_obj, "stock"):
            if product_obj.stock < quantity:
                return (False, f"موجودی کافی نیست. موجودی فعلی: {product_obj.stock}")
        return (True, None)

    return (False, "نوع محصول نامعتبر است")


def get_product_url(product_obj, product_type):
    """
    دریافت URL جزئیات محصول

    Args:
        product_obj: شیء محصول
        product_type (str): نوع محصول

    Returns:
        str: URL محصول
    """
    if hasattr(product_obj, "get_absolute_url"):
        return product_obj.get_absolute_url()
    return "#"


def serialize_cart_item(item):
    """
    تبدیل آیتم سبد به دیکشنری JSON-friendly
    برای استفاده در API ها

    Args:
        item (dict): آیتم سبد خرید

    Returns:
        dict: دیکشنری سریالایز شده
    """
    product_obj = item["product_obj"]
    product_type = item["product_type"]

    serialized = {
        "id": item["product_id"],
        "type": product_type,
        "quantity": item["quantity"],
        "total_price": float(item["total_price"]),
        "title": product_obj.title,
        "url": get_product_url(product_obj, product_type),
    }

    # افزودن اطلاعات خاص دوره
    if product_type == "course":
        serialized["course_details"] = {
            "instructor": (
                product_obj.instructor.get_full_name()
                if product_obj.instructor
                else None
            ),
            "duration": getattr(product_obj, "duration", None),
            "thumbnail": product_obj.thumbnail.url if product_obj.thumbnail else None,
        }

    # افزودن اطلاعات خاص محصول
    elif product_type == "product":
        serialized["product_details"] = {
            "category": product_obj.category.name if product_obj.category else None,
            "is_discounted": product_obj.is_discounted(),
            "discount_percentage": (
                product_obj.get_discount_percentage()
                if product_obj.is_discounted()
                else 0
            ),
            "original_price": float(product_obj.price),
            "final_price": float(product_obj.get_final_price()),
            "image": product_obj.image.url if product_obj.image else None,
        }

    return serialized


def get_cart_summary(cart_session):
    """
    دریافت خلاصه کامل سبد خرید

    Args:
        cart_session: نمونه CartSession

    Returns:
        dict: خلاصه سبد شامل آیتم‌ها و محاسبات
    """
    items = cart_session.get_cart_items()

    summary = {
        "items": [serialize_cart_item(item) for item in items],
        "total_items": cart_session.get_total_quantity(),
        "total_price": float(cart_session.get_total_payment_amount()),
        "formatted_total": format_price(cart_session.get_total_payment_amount()),
        "items_by_type": {
            "courses": [item for item in items if item["product_type"] == "course"],
            "products": [item for item in items if item["product_type"] == "product"],
        },
    }

    return summary


class CartValidator:
    """کلاس کمکی برای اعتبارسنجی سبد خرید"""

    @staticmethod
    def validate_cart_items(cart_session):
        """
        اعتبارسنجی تمام آیتم‌های سبد

        Returns:
            dict: {
                'is_valid': bool,
                'errors': list,
                'warnings': list
            }
        """
        errors = []
        warnings = []

        items = cart_session.get_cart_items()

        for item in items:
            product_obj = item["product_obj"]
            product_type = item["product_type"]

            # بررسی فعال بودن
            if not getattr(product_obj, "is_active", True):
                errors.append(f"{product_obj.title} غیرفعال شده است")

            # بررسی موجودی برای محصولات
            if product_type == "product":
                is_valid, error_msg = validate_product_stock(
                    product_obj, product_type, item["quantity"]
                )
                if not is_valid:
                    errors.append(f"{product_obj.title}: {error_msg}")

            # بررسی قیمت صفر
            if item["total_price"] == 0:
                warnings.append(f"{product_obj.title} قیمت صفر دارد")

        return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    @staticmethod
    def remove_invalid_items(cart_session):
        """حذف آیتم‌های نامعتبر از سبد"""
        validation = CartValidator.validate_cart_items(cart_session)

        if not validation["is_valid"]:
            items = cart_session.get_cart_items()
            for item in items:
                product_obj = item["product_obj"]
                if not getattr(product_obj, "is_active", True):
                    cart_session.remove_product(
                        item["product_id"], item["product_type"]
                    )

        return validation


# Decorator برای بررسی خالی نبودن سبد
def require_non_empty_cart(view_func):
    """
    دکوریتور برای اطمینان از خالی نبودن سبد

    استفاده:
    @require_non_empty_cart
    def checkout_view(request):
        ...
    """
    from functools import wraps
    from django.shortcuts import redirect
    from django.contrib import messages

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from cart.cart import CartSession

        cart = CartSession(request.session)

        if cart.get_total_quantity() == 0:
            messages.warning(request, "سبد خرید شما خالی است")
            return redirect("cart:cart_detail")

        return view_func(request, *args, **kwargs)

    return wrapper


# مثال استفاده از decorator:
"""
from cart.utils import require_non_empty_cart

@require_non_empty_cart
def checkout_view(request):
    # این view فقط زمانی اجرا می‌شود که سبد خرید خالی نباشد
    ...
"""
