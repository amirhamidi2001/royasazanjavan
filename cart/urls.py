from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    # Cart detail page
    path("", views.cart_detail_view, name="cart_detail"),
    # Cart actions
    path("add/<int:course_id>/", views.cart_add_view, name="cart_add"),
    path("remove/<int:course_id>/", views.cart_remove_view, name="cart_remove"),
    path("clear/", views.cart_clear_view, name="cart_clear"),
    # Cart sync (for logged-in users)
    path("sync/", views.cart_sync_view, name="cart_sync"),
    # AJAX endpoint for cart count
    path("count/", views.cart_count_view, name="cart_count"),
]
