from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Category, Tag, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Category model.
    Provides list display, slug auto-generation,
    and search functionality in the admin panel.
    """

    list_display = ["name", "slug", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin configuration for Tag model.
    Enables quick management and searching of tags.
    """

    list_display = ["name", "slug", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


class CommentInline(admin.TabularInline):
    """
    Inline admin configuration to display comments
    directly on the article admin detail page.
    """

    model = Comment
    extra = 0
    fields = ["name", "email", "body", "is_approved", "created_at"]
    readonly_fields = ["created_at"]
    can_delete = True


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Admin configuration for Article model.
    Includes advanced filtering, inline comments,
    bulk actions, and customized display fields.
    """

    list_display = [
        "title",
        "author",
        "status",
        "published_at",
        "view_count",
        "comment_count_display",
        "created_at",
    ]
    list_filter = ["status", "created_at", "published_at", "categories"]
    search_fields = ["title", "content", "excerpt"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    ordering = ["-published_at", "-created_at"]

    filter_horizontal = ["categories", "tags"]

    fieldsets = (
        (
            "Main Information",
            {"fields": ("title", "slug", "excerpt", "content", "featured_image")},
        ),
        ("Relationships", {"fields": ("author", "categories", "tags")}),
        ("Status & Dates", {"fields": ("status", "published_at")}),
        ("Statistics", {"fields": ("view_count",), "classes": ("collapse",)}),
    )

    readonly_fields = ["view_count"]
    inlines = [CommentInline]

    def comment_count_display(self, obj):
        """
        Display the number of approved comments for an article.
        Highlights the count in green if greater than zero.
        """
        count = obj.get_comment_count()
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>', count
            )
        return "0"

    comment_count_display.short_description = "Approved Comments"

    def save_model(self, request, obj, form, change):
        """
        Automatically assign the logged-in user as the author
        when creating a new article.
        """
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    actions = ["make_published", "make_draft"]

    def make_published(self, request, queryset):
        """
        Bulk action to publish selected articles.
        """
        updated = queryset.update(status="published")
        self.message_user(request, f"{updated} articles were published.")

    make_published.short_description = "Publish selected articles"

    def make_draft(self, request, queryset):
        """
        Bulk action to move selected articles back to draft status.
        """
        updated = queryset.update(status="draft")
        self.message_user(request, f"{updated} articles were moved to draft.")

    make_draft.short_description = "Mark selected articles as draft"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Comment model.
    Allows moderation, filtering, and bulk approval actions.
    """

    list_display = ["name", "email", "article", "is_approved", "created_at", "parent"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["name", "email", "body"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    fieldsets = (
        ("Author Information", {"fields": ("name", "email", "website")}),
        ("Content", {"fields": ("article", "body", "parent")}),
        ("Moderation Status", {"fields": ("is_approved",)}),
    )

    actions = ["approve_comments", "disapprove_comments"]

    def approve_comments(self, request, queryset):
        """
        Bulk action to approve selected comments.
        """
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} comments were approved.")

    approve_comments.short_description = "Approve selected comments"

    def disapprove_comments(self, request, queryset):
        """
        Bulk action to disapprove selected comments.
        """
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} comments were disapproved.")

    disapprove_comments.short_description = "Disapprove selected comments"
