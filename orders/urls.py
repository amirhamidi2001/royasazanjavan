from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout_view, name="checkout"),
    path("payment/<int:order_id>/", views.payment_view, name="payment"),
    path("payment/callback/", views.payment_callback_view, name="payment_callback"),
    path("success/<int:order_id>/", views.order_success_view, name="order_success"),
    path("detail/<int:order_id>/", views.order_detail_view, name="order_detail"),
    path("list/", views.order_list_view, name="order_list"),
    path("apply-coupon/", views.apply_coupon_view, name="apply_coupon"),
    path("remove-coupon/", views.remove_coupon_view, name="remove_coupon"),
]
