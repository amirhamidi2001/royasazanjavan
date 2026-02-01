from django.contrib import admin
from courses.models import Course, Video, CourseProgress, CourseRating


class VideoInline(admin.TabularInline):
    """Inline admin for videos within a course."""

    model = Video
    extra = 1
    fields = ["title", "video_link", "display_order", "duration"]
    ordering = ["display_order"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for Course model."""

    list_display = [
        "title",
        "instructor",
        "price",
        "duration",
        "is_active",
        "get_students_count",
        "created_date",
    ]
    list_filter = ["is_active", "created_date", "instructor"]
    search_fields = ["title", "description", "instructor__email"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["created_date", "updated_date"]
    inlines = [VideoInline]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "slug", "description", "instructor", "thumbnail")},
        ),
        ("Course Details", {"fields": ("duration", "price", "is_active")}),
        (
            "Timestamps",
            {"fields": ("created_date", "updated_date"), "classes": ("collapse",)},
        ),
    )

    def get_students_count(self, obj):
        return obj.get_students_count()

    get_students_count.short_description = "Students"


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for Video model."""

    list_display = ["title", "course", "display_order", "duration", "created_date"]
    list_filter = ["course", "created_date"]
    search_fields = ["title", "description", "course__title"]
    readonly_fields = ["created_date", "updated_date"]

    fieldsets = (
        (
            "Video Information",
            {"fields": ("course", "title", "video_link", "description")},
        ),
        ("Display Settings", {"fields": ("display_order", "duration")}),
        (
            "Timestamps",
            {"fields": ("created_date", "updated_date"), "classes": ("collapse",)},
        ),
    )


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    """Admin configuration for CourseProgress model."""

    list_display = [
        "user",
        "course",
        "completion_percentage",
        "enrolled_date",
        "last_accessed",
    ]
    list_filter = ["enrolled_date", "last_accessed", "course"]
    search_fields = ["user__email", "course__title"]
    readonly_fields = ["enrolled_date", "last_accessed"]
    filter_horizontal = ["watched_videos"]

    fieldsets = (
        (
            "Progress Information",
            {"fields": ("user", "course", "completion_percentage")},
        ),
        ("Watched Videos", {"fields": ("watched_videos",)}),
        (
            "Timestamps",
            {"fields": ("enrolled_date", "last_accessed"), "classes": ("collapse",)},
        ),
    )


@admin.register(CourseRating)
class CourseRatingAdmin(admin.ModelAdmin):
    """Admin configuration for CourseRating model."""

    list_display = ["user", "course", "rating", "created_date"]
    list_filter = ["rating", "created_date", "course"]
    search_fields = ["user__email", "course__title", "feedback"]
    readonly_fields = ["created_date", "updated_date"]

    fieldsets = (
        ("Rating Information", {"fields": ("user", "course", "rating", "feedback")}),
        (
            "Timestamps",
            {"fields": ("created_date", "updated_date"), "classes": ("collapse",)},
        ),
    )
