from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    # Product list with filtering
    path("", views.ProductListView.as_view(), name="product_list"),
    # Product detail
    path(
        "product/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"
    ),
]
