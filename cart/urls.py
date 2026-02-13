# cart/urls.py - نسخه بهبود یافته

from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    # Cart Display
    path("", views.cart_detail, name="cart_detail"),
    # Add to Cart (Form-based)
    path("add/course/<int:course_id>/", views.cart_add_course, name="cart_add_course"),
    path(
        "add/product/<int:product_id>/", views.cart_add_product, name="cart_add_product"
    ),
    # Remove from Cart
    path(
        "remove/<int:product_id>/<str:product_type>/",
        views.cart_remove,
        name="cart_remove",
    ),
    # Clear Cart
    path("clear/", views.cart_clear, name="cart_clear"),
    # AJAX Endpoints
    path("ajax/add/", views.cart_add_ajax, name="cart_add_ajax"),
    path("ajax/remove/", views.cart_remove_ajax, name="cart_remove_ajax"),
    path("ajax/count/", views.cart_count, name="cart_count"),
    path(
        "ajax/check/<int:product_id>/<str:product_type>/",
        views.check_item_in_cart,
        name="check_item_in_cart",
    ),
]
