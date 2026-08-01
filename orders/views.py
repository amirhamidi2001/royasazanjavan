import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from cart.cart import CartSession
from payments.exceptions import PaymentError
from payments.services import PaymentService

from .forms import CouponApplyForm, OrderCreateForm
from .models import Coupon, Order, OrderItem, OrderStatusChoices

logger = logging.getLogger("orders.payment")


@login_required
def checkout_view(request):
    """
    Display checkout page with order form and cart summary.
    Supports both courses and products.
    """
    cart = CartSession(request.session)
    cart_items = cart.get_cart_items()

    # Check if cart is empty
    if not cart_items:
        messages.warning(request, "سبد خرید شما خالی است")
        return redirect("cart:cart_detail")

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

    # Check if cart has physical products (requires address)
    has_physical_products = any(
        item["product_type"] == "product" for item in cart_items
    )

    if request.method == "POST":
        form = OrderCreateForm(request.POST, user=request.user)

        # Make address fields required if there are physical products
        if has_physical_products:
            for field in ["address", "city", "state", "zip_code"]:
                form.fields[field].required = True

        if form.is_valid():
            try:
                # Create order
                order = form.save(commit=False)
                order.user = request.user
                order.total_price = subtotal
                order.discount_amount = discount_amount
                order.tax_amount = tax_amount
                order.final_price = total
                order.save()

                # Create order items with Generic Foreign Keys
                for item in cart_items:
                    product_obj = item["product_obj"]
                    product_type = item["product_type"]

                    # Get appropriate ContentType
                    if product_type == "course":
                        from courses.models import Course

                        content_type = ContentType.objects.get_for_model(Course)
                    elif product_type == "product":
                        from shop.models import Product

                        content_type = ContentType.objects.get_for_model(Product)
                    else:
                        continue  # Skip unknown types

                    OrderItem.objects.create(
                        order=order,
                        content_type=content_type,
                        object_id=product_obj.id,
                        price=item["total_price"],  # Already calculated in cart
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
                messages.success(
                    request, f"سفارش شما با شماره {order.order_number} ثبت شد"
                )
                return redirect("orders:payment", order_id=order.id)

            except Exception as e:
                messages.error(request, f"خطا در ثبت سفارش: {str(e)}")
                return redirect("cart:cart_detail")
    else:
        # Pre-fill form with user data if available
        initial_data = {}
        # دسترسی به پروفایل از طریق related_name که در مدل تعریف کردید (user_profile)
        user_profile = getattr(request.user, "user_profile", None)

        if user_profile:
            if user_profile.first_name:
                initial_data["first_name"] = user_profile.first_name
            if user_profile.last_name:
                initial_data["last_name"] = user_profile.last_name

        # ایمیل مستقیماً در مدل User هست، پس اینجا مشکلی ندارد
        if request.user.email:
            initial_data["email"] = request.user.email

        form = OrderCreateForm(initial=initial_data, user=request.user)

    context = {
        "form": form,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "discount_amount": discount_amount,
        "total": total,
        "cart_count": len(cart_items),
        "has_physical_products": has_physical_products,
    }

    return render(request, "orders/checkout.html", context)


@login_required
def payment_view(request, order_id):
    """
    Initiate the payment process for an order using Zibal.

    This view is intentionally thin - all gateway logic lives in
    ``payments.services.PaymentService``.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not order.can_be_paid():
        messages.error(request, "این سفارش قابل پرداخت نیست")
        return redirect("orders:order_detail", order_id=order.id)

    callback_url = request.build_absolute_uri(reverse("orders:payment_callback"))

    try:
        redirect_url = PaymentService().initiate_payment(order, callback_url)
    except PaymentError as exc:
        logger.warning(
            "Payment initiation failed: order=%s error=%s", order.order_number, exc
        )
        messages.error(request, str(exc))
        return redirect("orders:order_detail", order_id=order.id)
    except Exception:
        logger.exception(
            "Unexpected error initiating payment: order=%s", order.order_number
        )
        messages.error(request, "خطا در اتصال به درگاه پرداخت. لطفاً مجدداً تلاش کنید")
        return redirect("orders:order_detail", order_id=order.id)

    return redirect(redirect_url)


@login_required
def payment_callback_view(request):
    """
    Handle the Zibal payment gateway callback and verify the transaction.

    Verification itself is fully delegated to
    ``payments.services.PaymentService``, which is idempotent and safe to
    call again for duplicate/retried callbacks.
    """
    track_id = request.GET.get("trackId")

    if not track_id:
        messages.error(request, "اطلاعات پرداخت نامعتبر است")
        return redirect("orders:order_list")

    order = Order.objects.filter(payment_track_id=track_id, user=request.user).first()

    if order is None:
        messages.error(request, "سفارش مورد نظر یافت نشد")
        return redirect("orders:order_list")

    # Zibal reports a user-cancelled/failed payment via success=0 before
    # any verification is attempted.
    if request.GET.get("success") == "0":
        order.status = OrderStatusChoices.CANCELLED
        order.save(update_fields=["status", "updated_date"])
        messages.warning(request, "پرداخت لغو شد")
        return redirect("orders:order_detail", order_id=order.id)

    service = PaymentService()

    try:
        success = service.verify_payment(order, request.GET)
    except PaymentError as exc:
        logger.warning(
            "Payment verification failed: order=%s error=%s", order.order_number, exc
        )
        messages.error(request, str(exc))
        return redirect("orders:order_detail", order_id=order.id)
    except Exception:
        logger.exception(
            "Unexpected error verifying payment: order=%s", order.order_number
        )
        messages.error(request, "خطا در تایید پرداخت")
        return redirect("orders:order_detail", order_id=order.id)

    if success:
        cart = CartSession(request.session)
        cart.clear()
        messages.success(
            request,
            f"پرداخت شما با موفقیت انجام شد. کد پیگیری: {order.payment_reference}",
        )
        return redirect("orders:order_success", order_id=order.id)

    messages.error(
        request,
        "پرداخت تایید نشد. در صورت کسر وجه، مبلغ به حساب شما بازگردانده می‌شود",
    )
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
    orders = Order.objects.filter(user=request.user).prefetch_related("items")

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
