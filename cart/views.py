from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from courses.models import Course
from cart.cart import CartSession


def cart_detail_view(request):
    """
    Display cart page with all items.
    """
    cart = CartSession(request.session)
    cart_items = cart.get_cart_items()

    context = {
        "cart_items": cart_items,
        "total_price": cart.get_total_payment_amount(),
        "total_quantity": cart.get_total_quantity(),
    }

    return render(request, "cart/cart_detail.html", context)


@require_POST
def cart_add_view(request, course_id):
    """
    Add a course to cart.
    Supports both regular POST and AJAX requests.
    """
    cart = CartSession(request.session)
    course = get_object_or_404(Course, id=course_id, is_active=True)

    # Add course to cart (returns False if already exists)
    added = cart.add_product(course_id)

    # Check if request is AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "added": added,
                "message": (
                    "دوره با موفقیت به سبد خرید اضافه شد"
                    if added
                    else "این دوره قبلاً به سبد خرید اضافه شده است"
                ),
                "cart_total_quantity": cart.get_total_quantity(),
                "cart_total_price": float(cart.get_total_payment_amount()),
            }
        )

    # Regular POST request
    if added:
        messages.success(request, f'دوره "{course.title}" به سبد خرید اضافه شد')
    else:
        messages.info(request, f'دوره "{course.title}" قبلاً در سبد خرید شما موجود است')

    return redirect("cart:cart_detail")


@require_POST
def cart_remove_view(request, course_id):
    """
    Remove a course from cart.
    Supports both regular POST and AJAX requests.
    """
    cart = CartSession(request.session)
    course = get_object_or_404(Course, id=course_id)

    cart.remove_product(course_id)

    # Check if request is AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "message": "دوره از سبد خرید حذف شد",
                "cart_total_quantity": cart.get_total_quantity(),
                "cart_total_price": float(cart.get_total_payment_amount()),
            }
        )

    # Regular POST request
    messages.success(request, f'دوره "{course.title}" از سبد خرید حذف شد')
    return redirect("cart:cart_detail")


@require_POST
def cart_clear_view(request):
    """
    Clear all items from cart.
    """
    cart = CartSession(request.session)
    cart.clear()

    # Check if request is AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "message": "سبد خرید خالی شد",
                "cart_total_quantity": 0,
                "cart_total_price": 0,
            }
        )

    messages.success(request, "سبد خرید با موفقیت خالی شد")
    return redirect("cart:cart_detail")


@login_required
def cart_sync_view(request):
    """
    Sync cart with database after login.
    This should be called automatically after user login.
    """
    cart = CartSession(request.session)
    cart.sync_cart_items_from_db(request.user)

    messages.success(request, "سبد خرید شما همگام‌سازی شد")
    return redirect("cart:cart_detail")


def cart_count_view(request):
    """
    AJAX endpoint to get current cart count.
    Used for updating header cart badge without page reload.
    """
    cart = CartSession(request.session)

    return JsonResponse(
        {
            "cart_total_quantity": cart.get_total_quantity(),
            "cart_total_price": float(cart.get_total_payment_amount()),
        }
    )
