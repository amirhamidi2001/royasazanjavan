from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    # Main display name of the category
    name = models.CharField(max_length=100, unique=True)

    # URL-friendly identifier generated from name
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    # Optional description for SEO or admin usage
    description = models.TextField(blank=True)

    # Timestamp when the category is created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        # Automatically generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    # Tag title displayed to users
    name = models.CharField(max_length=50, unique=True)

    # URL-friendly identifier generated from name
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    # Timestamp when the tag is created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        # Automatically generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PublishedManager(models.Manager):
    # Custom manager to return only published articles
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(status="published", published_at__lte=timezone.now())
        )


class Article(models.Model):
    # Possible publication states of an article
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )

    # Article headline
    title = models.CharField(max_length=250)

    # URL-friendly identifier generated from title
    slug = models.SlugField(max_length=250, unique=True, blank=True)

    # Short summary used in listings and previews
    excerpt = models.TextField(max_length=500)

    # Main article body
    content = models.TextField()

    # Primary image displayed with the article
    featured_image = models.ImageField(upload_to="articles/%Y/%m/%d/")

    # Author of the article
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="articles",
        verbose_name="Author",
    )

    # Categories assigned to the article
    categories = models.ManyToManyField(
        Category,
        related_name="articles",
        verbose_name="Categories",
    )

    # Optional tags for better classification
    tags = models.ManyToManyField(
        Tag,
        related_name="articles",
        blank=True,
        verbose_name="Tags",
    )

    # Publication status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="draft",
    )

    # Timestamps for lifecycle tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # Number of times the article has been viewed
    view_count = models.PositiveIntegerField(default=0)

    # Default and custom managers
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["-published_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["slug"]),
        ]

    def save(self, *args, **kwargs):
        # Generate slug from title if missing
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)

        # Automatically set publish date when publishing
        if self.status == "published" and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Canonical URL for article detail page
        return reverse("articles:article_detail", kwargs={"slug": self.slug})

    def increment_view_count(self):
        # Atomically increment view counter
        self.view_count = models.F("view_count") + 1
        self.save(update_fields=["view_count"])
        self.refresh_from_db()

    def get_approved_comments(self):
        # Return only approved comments related to this article
        return self.comments.filter(is_approved=True).select_related("article")

    def get_comment_count(self):
        # Count approved comments
        return self.comments.filter(is_approved=True).count()

    def get_reading_time(self):
        # Estimate reading time assuming 200 words per minute
        word_count = len(self.content.split())
        minutes = word_count // 200
        return max(1, minutes)


class Comment(models.Model):
    # Article to which this comment belongs
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Article",
    )

    # Comment author information
    name = models.CharField(max_length=80)
    email = models.EmailField()
    website = models.URLField(blank=True)

    # Comment text content
    body = models.TextField()

    # Moderation and timestamps
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Parent comment for threaded replies
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name="Reply to",
    )

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["is_approved"]),
        ]

    def __str__(self):
        return f"Comment by {self.name} on {self.article.title}"

    def get_replies(self):
        # Return approved child comments
        return self.replies.filter(is_approved=True)
