from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # Main dashboard
    path("", views.dashboard_view, name="dashboard"),
    # My Courses
    path("my-courses/", views.my_courses_view, name="my_courses"),
    # Orders
    path("my-orders/", views.my_orders_view, name="my_orders"),
    # Profile Settings
    path("profile/settings/", views.profile_settings_view, name="profile_settings"),
    # Account Settings
    path("account/settings/", views.account_settings_view, name="account_settings"),
    # Reviews
    path("my-reviews/", views.my_reviews_view, name="my_reviews"),
    path(
        "review/delete/<int:review_id>/", views.delete_review_view, name="delete_review"
    ),
    # Statistics
    path("statistics/", views.statistics_view, name="statistics"),
    # AJAX endpoints
    path(
        "upload-profile-image/",
        views.upload_profile_image_ajax,
        name="upload_profile_image",
    ),
]
