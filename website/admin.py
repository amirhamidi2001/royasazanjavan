from django.contrib import admin

from website.models import (
    ConsultationRequest,
    Contact,
    JobApplication,
    Newsletter,
)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Admin interface for managing contact form submissions."""

    date_hierarchy = "created_at"
    list_display = ("name", "email", "subject", "created_at")
    search_fields = ("name", "email", "subject", "message")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    """Admin interface for managing consultation requests."""

    list_display = (
        "name",
        "phone",
        "consultation_type",
        "subject",
        "created_at",
    )
    list_filter = ("consultation_type", "created_at")
    search_fields = ("name", "phone", "subject")
    readonly_fields = ("created_at",)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """Admin interface for managing job application submissions."""

    list_display = (
        "name",
        "phone",
        "education",
        "gender",
        "created_at",
    )
    list_filter = ("education", "gender", "marital_status")
    search_fields = ("name", "phone", "subject")
    readonly_fields = ("created_at",)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin interface for managing newsletter subscriptions."""

    list_display = ("email",)
    search_fields = ("email",)
