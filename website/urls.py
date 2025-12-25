from django.urls import path

from . import views

app_name = "website"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("faq/", views.FAQView.as_view(), name="faq"),
    path(
        "job/application/",
        views.JobApplicationView.as_view(),
        name="job-application",
    ),
    path("support/", views.SupportView.as_view(), name="support"),
    path("tos/", views.TosView.as_view(), name="tos"),
    path("404/", views.PageNotFoundView.as_view(), name="404"),
]
