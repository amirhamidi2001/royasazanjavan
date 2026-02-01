from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from accounts.models import User


class Course(models.Model):
    """Model representing an educational course."""

    title = models.CharField(_("course title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    description = models.TextField(_("description"))
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="taught_courses",
        verbose_name=_("instructor"),
    )
    duration = models.PositiveIntegerField(
        _("duration (hours)"), help_text=_("Total duration of the course in hours")
    )
    price = models.DecimalField(
        _("price"), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    thumbnail = models.ImageField(
        _("thumbnail"), upload_to="courses/thumbnails/", blank=True, null=True
    )
    is_active = models.BooleanField(_("is active"), default=True)
    students = models.ManyToManyField(
        User,
        through="CourseProgress",
        related_name="enrolled_courses",
        verbose_name=_("students"),
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("course")
        verbose_name_plural = _("courses")
        ordering = ["-created_date"]

    def __str__(self):
        return self.title

    def get_average_rating(self):
        """Calculate the average rating for this course."""
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 1)
        return 0

    def get_total_videos(self):
        """Return the total number of videos in this course."""
        return self.videos.count()

    def get_students_count(self):
        """Return the number of enrolled students."""
        return self.students.count()


class Video(models.Model):
    """Model representing a video within a course."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="videos",
        verbose_name=_("course"),
    )
    title = models.CharField(_("video title"), max_length=255)
    video_link = models.URLField(
        _("video link"), help_text=_("URL to the video (YouTube, Vimeo, etc.)")
    )
    description = models.TextField(_("description"), blank=True)
    display_order = models.PositiveIntegerField(
        _("display order"),
        default=0,
        help_text=_("Order in which the video appears in the course"),
    )
    duration = models.PositiveIntegerField(
        _("duration (minutes)"),
        help_text=_("Duration of the video in minutes"),
        default=0,
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("video")
        verbose_name_plural = _("videos")
        ordering = ["display_order", "created_date"]
        unique_together = ["course", "display_order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CourseProgress(models.Model):
    """Model to track user progress through a course."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="course_progress",
        verbose_name=_("user"),
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="student_progress",
        verbose_name=_("course"),
    )
    watched_videos = models.ManyToManyField(
        Video, related_name="watched_by", verbose_name=_("watched videos"), blank=True
    )
    completion_percentage = models.PositiveIntegerField(
        _("completion percentage"),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    enrolled_date = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("course progress")
        verbose_name_plural = _("course progress")
        unique_together = ["user", "course"]
        ordering = ["-last_accessed"]

    def __str__(self):
        return (
            f"{self.user.email} - {self.course.title} ({self.completion_percentage}%)"
        )

    def update_progress(self):
        """Calculate and update the completion percentage."""
        total_videos = self.course.get_total_videos()
        if total_videos > 0:
            watched_count = self.watched_videos.count()
            self.completion_percentage = int((watched_count / total_videos) * 100)
            self.save()

    def mark_video_watched(self, video):
        """Mark a video as watched and update progress."""
        if video.course == self.course:
            self.watched_videos.add(video)
            self.update_progress()


class CourseRating(models.Model):
    """Model for user ratings and reviews of courses."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="course_ratings",
        verbose_name=_("user"),
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name=_("course"),
    )
    rating = models.PositiveIntegerField(
        _("rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("Rate from 1 to 5 stars"),
    )
    feedback = models.TextField(_("feedback"))

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("course rating")
        verbose_name_plural = _("course ratings")
        unique_together = ["user", "course"]
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.rating}★)"
