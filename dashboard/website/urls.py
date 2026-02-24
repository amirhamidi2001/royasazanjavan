# dashboard/website/urls.py
from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
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
    path("contacts/", views.ContactListView.as_view(), name="contact-list"),
    path(
        "contacts/<int:pk>/delete/",
        views.ContactDeleteView.as_view(),
        name="contact-delete",
    ),
    path("jobs/", views.JobApplicationListView.as_view(), name="job-list"),
    path(
        "jobs/<int:pk>/delete/",
        views.JobApplicationDeleteView.as_view(),
        name="job-delete",
    ),
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
    path(
        "partners/",
        views.PartnerCompanyListView.as_view(),
        name="partner-list",
    ),
    path(
        "partners/create/",
        views.PartnerCompanyCreateView.as_view(),
        name="partner-create",
    ),
    path(
        "partners/<int:pk>/edit/",
        views.PartnerCompanyUpdateView.as_view(),
        name="partner-update",
    ),
    path(
        "partners/<int:pk>/delete/",
        views.PartnerCompanyDeleteView.as_view(),
        name="partner-delete",
    ),
]
