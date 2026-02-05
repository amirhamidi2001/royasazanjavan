# dashboard/website/urls.py
from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    # Consultation URLs
    path(
        "consultations/",
        views.ConsultationRequestListView.as_view(),
        name="consultation-list",
    ),
    path(
        "consultations/<int:pk>/delete/",
        views.ConsultationRequestDeleteView.as_view(),
        name="consultation-delete",
    ),
    # Contact URLs
    path("contacts/", views.ContactListView.as_view(), name="contact-list"),
    path(
        "contacts/<int:pk>/delete/",
        views.ContactDeleteView.as_view(),
        name="contact-delete",
    ),
    # Job Application URLs
    path("jobs/", views.JobApplicationListView.as_view(), name="job-list"),
    path(
        "jobs/<int:pk>/delete/",
        views.JobApplicationDeleteView.as_view(),
        name="job-delete",
    ),
    # Newsletter URLs
    path(
        "newsletters/",
        views.NewsletterListView.as_view(),
        name="newsletter-list",
    ),
    path(
        "newsletters/<int:pk>/delete/",
        views.NewsletterDeleteView.as_view(),
        name="newsletter-delete",
    ),
]
