from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    # Course URLs
    path("courses/", views.CourseListView.as_view(), name="course-list"),
    path("courses/create/", views.CourseCreateView.as_view(), name="course-create"),
    path(
        "courses/<int:pk>/update/",
        views.CourseUpdateView.as_view(),
        name="course-update",
    ),
    path(
        "courses/<int:pk>/delete/",
        views.CourseDeleteView.as_view(),
        name="course-delete",
    ),
    # Video URLs
    path("videos/", views.VideoListView.as_view(), name="video-list"),
    path("videos/create/", views.VideoCreateView.as_view(), name="video-create"),
    path(
        "videos/<int:pk>/update/", views.VideoUpdateView.as_view(), name="video-update"
    ),
    path(
        "videos/<int:pk>/delete/", views.VideoDeleteView.as_view(), name="video-delete"
    ),
    # Progress URLs
    path("progress/", views.CourseProgressListView.as_view(), name="progress-list"),
    path(
        "progress/<int:pk>/delete/",
        views.CourseProgressDeleteView.as_view(),
        name="progress-delete",
    ),
    # Rating URLs
    path("ratings/", views.CourseRatingListView.as_view(), name="rating-list"),
    path(
        "ratings/<int:pk>/update/",
        views.CourseRatingUpdateView.as_view(),
        name="rating-update",
    ),
    path(
        "ratings/<int:pk>/delete/",
        views.CourseRatingDeleteView.as_view(),
        name="rating-delete",
    ),
]
