from django.urls import include, path

app_name = "dashboard"

urlpatterns = [
    path("", include("dashboard.customers.urls")),
    path("accounts/", include("dashboard.accounts.urls")),
    path("articles/", include("dashboard.articles.urls")),
    path("courses/", include("dashboard.courses.urls")),
    path("cart/", include("dashboard.cart.urls")),
    path("orders/", include("dashboard.orders.urls")),
    path("shop/", include("dashboard.shop.urls")),
    path("website/", include("dashboard.website.urls")),
]
