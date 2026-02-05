from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # User URLs
    path("users/", views.UserListView.as_view(), name="user-list"),
    path("users/create/", views.UserCreateView.as_view(), name="user-create"),
    path("users/<int:pk>/update/", views.UserUpdateView.as_view(), name="user-update"),
    path("users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="user-delete"),
    # Profile URLs
    path("profiles/", views.ProfileListView.as_view(), name="profile-list"),
    path(
        "profiles/<int:pk>/update/",
        views.ProfileUpdateView.as_view(),
        name="profile-update",
    ),
    path(
        "profiles/<int:pk>/delete/",
        views.ProfileDeleteView.as_view(),
        name="profile-delete",
    ),
]
