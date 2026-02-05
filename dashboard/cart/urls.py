# dashboard/cart/urls.py
from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("carts/", views.CartListView.as_view(), name="cart-list"),
    path(
        "carts/<int:pk>/delete/",
        views.CartDeleteView.as_view(),
        name="cart-delete",
    ),
]
