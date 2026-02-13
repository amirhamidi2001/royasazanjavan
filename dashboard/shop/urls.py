from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    # Category URLs
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path(
        "categories/create/", views.CategoryCreateView.as_view(), name="category-create"
    ),
    path(
        "categories/<int:pk>/update/",
        views.CategoryUpdateView.as_view(),
        name="category-update",
    ),
    path(
        "categories/<int:pk>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category-delete",
    ),
    # Product URLs
    path("products/", views.ProductListView.as_view(), name="product-list"),
    path("products/create/", views.ProductCreateView.as_view(), name="product-create"),
    path(
        "products/<int:pk>/update/",
        views.ProductUpdateView.as_view(),
        name="product-update",
    ),
    path(
        "products/<int:pk>/delete/",
        views.ProductDeleteView.as_view(),
        name="product-delete",
    ),
    # Product Feature URLs
    path("features/", views.ProductFeatureListView.as_view(), name="feature-list"),
    path(
        "features/create/",
        views.ProductFeatureCreateView.as_view(),
        name="feature-create",
    ),
    path(
        "features/<int:pk>/update/",
        views.ProductFeatureUpdateView.as_view(),
        name="feature-update",
    ),
    path(
        "features/<int:pk>/delete/",
        views.ProductFeatureDeleteView.as_view(),
        name="feature-delete",
    ),
]
