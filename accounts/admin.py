from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.sessions.models import Session
from django.utils.translation import gettext_lazy as _
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    """
    Inline display for the user's Profile model.
    """

    model = Profile
    can_delete = False
    verbose_name_plural = _("Profile")
    fk_name = "user"
    fields = (
        "first_name",
        "last_name",
        "phone_number",
        "image",
        "created_date",
        "updated_date",
    )
    readonly_fields = ("created_date", "updated_date")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User model configuration for Django admin.
    """

    inlines = [ProfileInline]

    list_display = (
        "email",
        "is_active",
        "is_verified",
        "is_staff",
        "is_superuser",
        "type",
        "created_date",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "is_verified", "type")
    search_fields = ("email", "user_profile__first_name", "user_profile__last_name")
    ordering = ("-created_date",)
    readonly_fields = ("created_date", "updated_date")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("User Type"), {"fields": ("type",)}),
        (
            _("Important dates"),
            {"fields": ("last_login", "created_date", "updated_date")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "type",
                ),
            },
        ),
    )

    def get_inline_instances(self, request, obj=None):
        """Show inlines only for existing users."""
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Separate admin interface for Profiles (optional if inline used).
    """

    list_display = ("user", "get_fullname", "phone_number", "created_date")
    search_fields = ("user__email", "first_name", "last_name", "phone_number")
    readonly_fields = ("created_date", "updated_date")
    ordering = ("-created_date",)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()

    list_display = ("session_key", "_session_data", "expire_date")
    readonly_fields = ("_session_data",)
