from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    # Order URLs
    path("orders/", views.OrderListView.as_view(), name="order-list"),
    path(
        "orders/<int:pk>/update/",
        views.OrderUpdateView.as_view(),
        name="order-update",
    ),
    path(
        "orders/<int:pk>/delete/",
        views.OrderDeleteView.as_view(),
        name="order-delete",
    ),
    # Coupon URLs
    path("coupons/", views.CouponListView.as_view(), name="coupon-list"),
    path("coupons/create/", views.CouponCreateView.as_view(), name="coupon-create"),
    path(
        "coupons/<int:pk>/update/",
        views.CouponUpdateView.as_view(),
        name="coupon-update",
    ),
    path(
        "coupons/<int:pk>/delete/",
        views.CouponDeleteView.as_view(),
        name="coupon-delete",
    ),
]
