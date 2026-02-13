# cart/views.py - نسخه بهبود یافته با مدیریت خطا و AJAX

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from cart.cart import CartSession
from courses.models import Course
from shop.models import Product


def is_ajax(request):
    """بررسی AJAX request"""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def cart_detail(request):
    """نمایش جزئیات سبد خرید"""
    try:
        cart = CartSession(request.session)
        cart_items = cart.get_cart_items()
        total_payment = cart.get_total_payment_amount()

        context = {
            "cart_items": cart_items,
            "total_payment": total_payment,
            "total_quantity": cart.get_total_quantity(),
        }
        return render(request, "cart/cart_detail.html", context)
    except Exception as e:
        messages.error(request, f"خطا در بارگذاری سبد خرید: {str(e)}")
        return render(
            request,
            "cart/cart_detail.html",
            {
                "cart_items": [],
                "total_payment": 0,
                "total_quantity": 0,
            },
        )


@require_POST
def cart_add_course(request, course_id):
    """افزودن دوره به سبد خرید"""
    try:
        course = get_object_or_404(Course, id=course_id, is_active=True)
        cart = CartSession(request.session)

        # افزودن دوره به سبد خرید
        added = cart.add_product(course_id, product_type="course")

        if is_ajax(request):
            return JsonResponse(
                {
                    "success": True,
                    "added": added,
                    "message": (
                        f'دوره "{course.title}" به سبد خرید اضافه شد.'
                        if added
                        else f'دوره "{course.title}" قبلاً در سبد خرید موجود است.'
                    ),
                    "cart_quantity": cart.get_total_quantity(),
                    "cart_total": float(cart.get_total_payment_amount()),
                }
            )

        if added:
            messages.success(request, f'دوره "{course.title}" به سبد خرید اضافه شد.')
        else:
            messages.info(request, f'دوره "{course.title}" قبلاً در سبد خرید موجود است.')

        next_url = request.POST.get(
            "next", request.META.get("HTTP_REFERER", "cart:cart_detail")
        )
        return redirect(next_url)

    except Course.DoesNotExist:
        if is_ajax(request):
            return JsonResponse(
                {"success": False, "message": "دوره مورد نظر یافت نشد یا غیرفعال است."},
                status=404,
            )

        messages.error(request, "دوره مورد نظر یافت نشد یا غیرفعال است.")
        return redirect("courses:course_list")

    except Exception as e:
        if is_ajax(request):
            return JsonResponse(
                {"success": False, "message": f"خطا در افزودن به سبد خرید: {str(e)}"},
                status=500,
            )

        messages.error(request, f"خطا در افزودن به سبد خرید: {str(e)}")
        return redirect("cart:cart_detail")


@require_POST
def cart_add_product(request, product_id):
    """افزودن محصول به سبد خرید"""
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = CartSession(request.session)

        # بررسی موجودی
        if hasattr(product, "stock") and product.stock < 1:
            error_msg = f'محصول "{product.title}" موجود نیست.'
            if is_ajax(request):
                return JsonResponse(
                    {"success": False, "message": error_msg}, status=400
                )

            messages.error(request, error_msg)
            return redirect(request.META.get("HTTP_REFERER", "shop:product_list"))

        # افزودن محصول به سبد خرید
        added = cart.add_product(product_id, product_type="product")

        if is_ajax(request):
            return JsonResponse(
                {
                    "success": True,
                    "added": added,
                    "message": (
                        f'محصول "{product.title}" به سبد خرید اضافه شد.'
                        if added
                        else f'محصول "{product.title}" قبلاً در سبد خرید موجود است.'
                    ),
                    "cart_quantity": cart.get_total_quantity(),
                    "cart_total": float(cart.get_total_payment_amount()),
                }
            )

        if added:
            messages.success(request, f'محصول "{product.title}" به سبد خرید اضافه شد.')
        else:
            messages.info(
                request, f'محصول "{product.title}" قبلاً در سبد خرید موجود است.'
            )

        next_url = request.POST.get(
            "next", request.META.get("HTTP_REFERER", "cart:cart_detail")
        )
        return redirect(next_url)

    except Product.DoesNotExist:
        if is_ajax(request):
            return JsonResponse(
                {
                    "success": False,
                    "message": "محصول مورد نظر یافت نشد یا غیرفعال است.",
                },
                status=404,
            )

        messages.error(request, "محصول مورد نظر یافت نشد یا غیرفعال است.")
        return redirect("shop:product_list")

    except Exception as e:
        if is_ajax(request):
            return JsonResponse(
                {"success": False, "message": f"خطا در افزودن به سبد خرید: {str(e)}"},
                status=500,
            )

        messages.error(request, f"خطا در افزودن به سبد خرید: {str(e)}")
        return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id, product_type):
    """حذف آیتم از سبد خرید"""
    try:
        cart = CartSession(request.session)

        # بررسی معتبر بودن product_type
        if product_type not in ["course", "product"]:
            raise ValueError("نوع محصول نامعتبر است")

        # حذف محصول
        cart.remove_product(product_id, product_type)

        if is_ajax(request):
            return JsonResponse(
                {
                    "success": True,
                    "message": "محصول از سبد خرید حذف شد.",
                    "cart_quantity": cart.get_total_quantity(),
                    "cart_total": float(cart.get_total_payment_amount()),
                }
            )

        messages.success(request, "محصول از سبد خرید حذف شد.")
        return redirect("cart:cart_detail")

    except ValueError as e:
        if is_ajax(request):
            return JsonResponse({"success": False, "message": str(e)}, status=400)

        messages.error(request, str(e))
        return redirect("cart:cart_detail")

    except Exception as e:
        if is_ajax(request):
            return JsonResponse(
                {"success": False, "message": f"خطا در حذف محصول: {str(e)}"}, status=500
            )

        messages.error(request, f"خطا در حذف محصول: {str(e)}")
        return redirect("cart:cart_detail")


@require_POST
def cart_clear(request):
    """پاک کردن تمام سبد خرید"""
    try:
        cart = CartSession(request.session)
        cart.clear()

        if is_ajax(request):
            return JsonResponse(
                {
                    "success": True,
                    "message": "سبد خرید خالی شد.",
                    "cart_quantity": 0,
                    "cart_total": 0,
                }
            )

        messages.success(request, "سبد خرید خالی شد.")
        return redirect("cart:cart_detail")

    except Exception as e:
        if is_ajax(request):
            return JsonResponse(
                {"success": False, "message": f"خطا در خالی کردن سبد خرید: {str(e)}"},
                status=500,
            )

        messages.error(request, f"خطا در خالی کردن سبد خرید: {str(e)}")
        return redirect("cart:cart_detail")


# AJAX Views


@require_POST
def cart_add_ajax(request):
    """افزودن به سبد خرید با AJAX"""
    try:
        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # Fallback to POST data
            data = request.POST

        product_id = data.get("product_id")
        product_type = data.get("product_type", "course")

        if not product_id:
            return JsonResponse(
                {"success": False, "message": "شناسه محصول الزامی است."}, status=400
            )

        # Validate product type
        if product_type not in ["course", "product"]:
            return JsonResponse(
                {"success": False, "message": "نوع محصول نامعتبر است."}, status=400
            )

        cart = CartSession(request.session)

        # Get product object for validation
        if product_type == "course":
            try:
                product_obj = Course.objects.get(id=product_id, is_active=True)
                product_name = product_obj.title
            except Course.DoesNotExist:
                return JsonResponse(
                    {"success": False, "message": "دوره مورد نظر یافت نشد."}, status=404
                )
        else:
            try:
                product_obj = Product.objects.get(id=product_id, is_active=True)
                product_name = product_obj.title

                # Check stock
                if hasattr(product_obj, "stock") and product_obj.stock < 1:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": f'محصول "{product_name}" موجود نیست.',
                        },
                        status=400,
                    )
            except Product.DoesNotExist:
                return JsonResponse(
                    {"success": False, "message": "محصول مورد نظر یافت نشد."},
                    status=404,
                )

        # Add to cart
        added = cart.add_product(product_id, product_type)

        return JsonResponse(
            {
                "success": True,
                "added": added,
                "message": (
                    f'"{product_name}" به سبد خرید اضافه شد.'
                    if added
                    else f'"{product_name}" قبلاً در سبد خرید موجود است.'
                ),
                "cart_quantity": cart.get_total_quantity(),
                "cart_total": float(cart.get_total_payment_amount()),
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"خطای سیستم: {str(e)}"}, status=500
        )


@require_POST
def cart_remove_ajax(request):
    """حذف از سبد خرید با AJAX"""
    try:
        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST

        product_id = data.get("product_id")
        product_type = data.get("product_type", "course")

        if not product_id:
            return JsonResponse(
                {"success": False, "message": "شناسه محصول الزامی است."}, status=400
            )

        cart = CartSession(request.session)
        cart.remove_product(product_id, product_type)

        return JsonResponse(
            {
                "success": True,
                "message": "محصول از سبد خرید حذف شد.",
                "cart_quantity": cart.get_total_quantity(),
                "cart_total": float(cart.get_total_payment_amount()),
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"خطا در حذف: {str(e)}"}, status=500
        )


def cart_count(request):
    """دریافت تعداد آیتم‌های سبد خرید (برای AJAX)"""
    try:
        cart = CartSession(request.session)
        return JsonResponse(
            {
                "success": True,
                "cart_quantity": cart.get_total_quantity(),
                "cart_total": float(cart.get_total_payment_amount()),
            }
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": str(e), "cart_quantity": 0, "cart_total": 0}
        )


def check_item_in_cart(request, product_id, product_type):
    """بررسی وجود آیتم در سبد خرید"""
    try:
        cart = CartSession(request.session)
        in_cart = cart.is_product_in_cart(product_id, product_type)

        return JsonResponse({"success": True, "in_cart": in_cart})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e), "in_cart": False})
