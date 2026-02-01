from django.urls import path
from courses.views import (
    CourseListView,
    CourseDetailView,
    SubmitRatingView,
    CourseProgressView,
    MarkVideoWatchedView,
    EnrollCourseView,
)

app_name = "courses"

urlpatterns = [
    path("", CourseListView.as_view(), name="course_list"),
    path("<slug:slug>/", CourseDetailView.as_view(), name="course_detail"),
    path("<slug:slug>/enroll/", EnrollCourseView.as_view(), name="enroll_course"),
    path("<slug:slug>/rate/", SubmitRatingView.as_view(), name="submit_rating"),
    path(
        "<slug:slug>/video/<int:video_id>/watched/",
        MarkVideoWatchedView.as_view(),
        name="mark_video_watched",
    ),
    path("my/progress/", CourseProgressView.as_view(), name="course_progress"),
]
