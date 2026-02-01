from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.urls import reverse
from decimal import Decimal
import requests
import json

from cart.cart import CartSession
from .models import Order, OrderItem, Coupon, OrderStatusChoices
from .forms import OrderCreateForm, CouponApplyForm


# ZarinPal Configuration
ZARINPAL_MERCHANT_ID = getattr(settings, "ZARINPAL_MERCHANT_ID", "YOUR-MERCHANT-ID")
ZARINPAL_WEBGATE = "https://www.zarinpal.com/pg/StartPay/"
ZARINPAL_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZARINPAL_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"


@login_required
def checkout_view(request):
    """
    Display checkout page with order form and cart summary.
    """
    cart = CartSession(request.session)
    cart_items = cart.get_cart_items()

    # Check if cart is empty
    if not cart_items:
        messages.warning(request, "سبد خرید شما خالی است")
        return redirect("courses:course_list")

    # Calculate totals
    subtotal = cart.get_total_payment_amount()
    tax_amount = Decimal("0")  # For educational courses, usually no tax
    discount_amount = Decimal("0")

    # Check for coupon in session
    coupon_id = request.session.get("coupon_id")
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            if coupon.can_use(subtotal):
                discount_amount = Decimal(
                    str(coupon.calculate_discount(float(subtotal)))
                )
        except Coupon.DoesNotExist:
            del request.session["coupon_id"]

    total = subtotal - discount_amount + tax_amount

    if request.method == "POST":
        form = OrderCreateForm(request.POST, user=request.user)
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = subtotal
            order.discount_amount = discount_amount
            order.tax_amount = tax_amount
            order.final_price = total
            order.save()

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    course=item["course_obj"],
                    price=item["course_obj"].price,
                    quantity=item["quantity"],
                )

            # Apply coupon if exists
            if coupon_id:
                try:
                    coupon = Coupon.objects.get(id=coupon_id)
                    coupon.use_coupon()
                    del request.session["coupon_id"]
                except Coupon.DoesNotExist:
                    pass

            # Redirect to payment
            messages.success(request, f"سفارش شما با شماره {order.order_number} ثبت شد")
            return redirect("orders:payment", order_id=order.id)
    else:
        form = OrderCreateForm(user=request.user)

    context = {
        "form": form,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "discount_amount": discount_amount,
        "total": total,
        "cart_count": len(cart_items),
    }

    return render(request, "orders/checkout.html", context)


@login_required
def payment_view(request, order_id):
    """
    Initiate payment process with ZarinPal.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Check if order can be paid
    if not order.can_be_paid():
        messages.error(request, "این سفارش قابل پرداخت نیست")
        return redirect("orders:order_detail", order_id=order.id)

    # Prepare payment request
    amount = int(order.final_price)  # ZarinPal expects Toman
    description = f"پرداخت سفارش {order.order_number}"
    callback_url = request.build_absolute_uri(reverse("orders:payment_callback"))

    # Request payment from ZarinPal
    request_data = {
        "merchant_id": ZARINPAL_MERCHANT_ID,
        "amount": amount,
        "description": description,
        "callback_url": callback_url,
        "metadata": {"email": order.email, "mobile": order.phone},
    }

    try:
        response = requests.post(ZARINPAL_API_REQUEST, json=request_data, timeout=10)
        response_data = response.json()

        if response_data.get("data") and response_data["data"].get("code") == 100:
            # Success - save authority and redirect to payment gateway
            authority = response_data["data"]["authority"]
            order.zarinpal_authority = authority
            order.status = OrderStatusChoices.PROCESSING
            order.save()

            # Redirect to ZarinPal payment page
            payment_url = f"{ZARINPAL_WEBGATE}{authority}"
            return redirect(payment_url)
        else:
            # Error from ZarinPal
            error_message = response_data.get("errors", {}).get(
                "message", "خطا در اتصال به درگاه پرداخت"
            )
            messages.error(request, error_message)
            order.status = OrderStatusChoices.FAILED
            order.save()

    except requests.exceptions.RequestException as e:
        messages.error(request, "خطا در اتصال به درگاه پرداخت. لطفاً مجدداً تلاش کنید")
        order.status = OrderStatusChoices.FAILED
        order.save()

    return redirect("orders:order_detail", order_id=order.id)


@login_required
def payment_callback_view(request):
    """
    Handle payment callback from ZarinPal.
    """
    authority = request.GET.get("Authority")
    status = request.GET.get("Status")

    if not authority:
        messages.error(request, "اطلاعات پرداخت نامعتبر است")
        return redirect("orders:order_list")

    try:
        order = Order.objects.get(zarinpal_authority=authority, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, "سفارش مورد نظر یافت نشد")
        return redirect("orders:order_list")

    # Check payment status
    if status == "OK":
        # Verify payment with ZarinPal
        verify_data = {
            "merchant_id": ZARINPAL_MERCHANT_ID,
            "amount": int(order.final_price),
            "authority": authority,
        }

        try:
            response = requests.post(ZARINPAL_API_VERIFY, json=verify_data, timeout=10)
            response_data = response.json()

            if response_data.get("data") and response_data["data"].get("code") == 100:
                # Payment verified successfully
                ref_id = response_data["data"]["ref_id"]
                order.mark_as_paid(ref_id)

                # Clear cart
                cart = CartSession(request.session)
                cart.clear()

                messages.success(
                    request, f"پرداخت شما با موفقیت انجام شد. کد پیگیری: {ref_id}"
                )
                return redirect("orders:order_success", order_id=order.id)
            else:
                # Verification failed
                order.status = OrderStatusChoices.FAILED
                order.save()
                messages.error(
                    request,
                    "پرداخت تایید نشد. در صورت کسر وجه، مبلغ به حساب شما بازگردانده می‌شود",
                )

        except requests.exceptions.RequestException:
            order.status = OrderStatusChoices.FAILED
            order.save()
            messages.error(request, "خطا در تایید پرداخت")
    else:
        # Payment cancelled by user
        order.status = OrderStatusChoices.CANCELLED
        order.save()
        messages.warning(request, "پرداخت لغو شد")

    return redirect("orders:order_detail", order_id=order.id)


@login_required
def order_success_view(request, order_id):
    """Display order success page."""
    order = get_object_or_404(Order, id=order_id, user=request.user, is_paid=True)

    context = {
        "order": order,
    }

    return render(request, "orders/order_success.html", context)


@login_required
def order_detail_view(request, order_id):
    """Display order details."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    context = {
        "order": order,
    }

    return render(request, "orders/order_detail.html", context)


@login_required
def order_list_view(request):
    """Display user's order history."""
    orders = Order.objects.filter(user=request.user)

    context = {
        "orders": orders,
    }

    return render(request, "orders/order_list.html", context)


@login_required
@require_POST
def apply_coupon_view(request):
    """Apply coupon code to cart (AJAX)."""
    cart = CartSession(request.session)
    subtotal = cart.get_total_payment_amount()

    form = CouponApplyForm(request.POST, total_amount=float(subtotal))

    if form.is_valid():
        code = form.cleaned_data["code"]
        coupon = form.coupon
        discount_amount = form.get_discount_amount()

        # Save coupon to session
        request.session["coupon_id"] = coupon.id
        request.session["coupon_code"] = code
        request.session["discount_amount"] = float(discount_amount)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "message": "کد تخفیف با موفقیت اعمال شد",
                    "discount_amount": float(discount_amount),
                    "total": float(subtotal - Decimal(str(discount_amount))),
                }
            )

        messages.success(request, "کد تخفیف با موفقیت اعمال شد")
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "message": form.errors.get("code", ["کد تخفیف نامعتبر است"])[0],
                }
            )

        messages.error(request, form.errors.get("code", ["کد تخفیف نامعتبر است"])[0])

    return redirect("orders:checkout")


@login_required
@require_POST
def remove_coupon_view(request):
    """Remove applied coupon from session."""
    if "coupon_id" in request.session:
        del request.session["coupon_id"]
    if "coupon_code" in request.session:
        del request.session["coupon_code"]
    if "discount_amount" in request.session:
        del request.session["discount_amount"]

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True, "message": "کد تخفیف حذف شد"})

    messages.success(request, "کد تخفیف حذف شد")
    return redirect("orders:checkout")
