from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from courses.models import Course, Video, CourseProgress, CourseRating
from dashboard.mixins import (
    DashboardMixin,
    SuccessMessageMixin,
    DeleteSuccessMessageMixin,
)


class CourseListView(DashboardMixin, ListView):
    """Dashboard view for listing all courses with search and status filters."""

    model = Course
    template_name = "dashboard/courses/course_list.html"
    context_object_name = "courses"
    paginate_by = 20
    ordering = ["-created_date"]

    def get_queryset(self):
        """Return optimized queryset with instructor and student count, filtered by search/status."""
        queryset = (
            super()
            .get_queryset()
            .select_related("instructor")
            .annotate(total_students=Count("students"))
        )
        search_query = self.request.GET.get("search", "")
        status_filter = self.request.GET.get("status", "")

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(instructor__email__icontains=search_query)
            )

        if status_filter == "active":
            queryset = queryset.filter(is_active=True)
        elif status_filter == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        """Add search query, status filter, title and create URL to template context."""
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["title"] = "مدیریت دوره‌ها"
        context["create_url"] = reverse_lazy("dashboard:courses:course-create")
        return context


class CourseCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """Dashboard view for creating a new course with success message."""

    model = Course
    template_name = "dashboard/courses/course_form.html"
    fields = [
        "title",
        "slug",
        "description",
        "instructor",
        "duration",
        "price",
        "thumbnail",
        "is_active",
    ]
    success_url = reverse_lazy("dashboard:courses:course-list")
    success_message = "دوره با موفقیت ایجاد شد."

    def get_context_data(self, **kwargs):
        """Add title and submit button text to the course creation form context."""
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد دوره جدید"
        context["submit_text"] = "ایجاد دوره"
        return context


class CourseUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """Dashboard view for updating an existing course with success message."""

    model = Course
    template_name = "dashboard/courses/course_form.html"
    fields = [
        "title",
        "slug",
        "description",
        "instructor",
        "duration",
        "price",
        "thumbnail",
        "is_active",
    ]
    success_url = reverse_lazy("dashboard:courses:course-list")
    success_message = "دوره با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        """Add title and submit button text to the course update form context."""
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش دوره"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class CourseDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """Dashboard view for deleting a course with confirmation and success message."""

    model = Course
    template_name = "dashboard/courses/course_confirm_delete.html"
    success_url = reverse_lazy("dashboard:courses:course-list")
    delete_success_message = "دوره با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        """Add title to the course delete confirmation template context."""
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف دوره"
        return context


class VideoListView(DashboardMixin, ListView):
    """Dashboard view for listing all videos with search and course filters."""

    model = Video
    template_name = "dashboard/courses/video_list.html"
    context_object_name = "videos"
    paginate_by = 20
    ordering = ["course", "display_order"]

    def get_queryset(self):
        """Return optimized queryset with course data, filtered by search and course ID."""
        queryset = super().get_queryset().select_related("course")
        search_query = self.request.GET.get("search", "")
        course_filter = self.request.GET.get("course", "")

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(course__title__icontains=search_query)
            )

        if course_filter:
            queryset = queryset.filter(course_id=course_filter)

        return queryset

    def get_context_data(self, **kwargs):
        """Add search query, course filter, courses list, title and create URL to context."""
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["course_filter"] = self.request.GET.get("course", "")
        context["courses"] = Course.objects.all()
        context["title"] = "مدیریت ویدیوها"
        context["create_url"] = reverse_lazy("dashboard:courses:video-create")
        return context


class VideoCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """Dashboard view for creating a new video with success message."""

    model = Video
    template_name = "dashboard/courses/video_form.html"
    fields = [
        "course",
        "title",
        "video_link",
        "description",
        "display_order",
        "duration",
    ]
    success_url = reverse_lazy("dashboard:courses:video-list")
    success_message = "ویدیو با موفقیت ایجاد شد."

    def get_context_data(self, **kwargs):
        """Add title and submit button text to the video creation form context."""
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد ویدیو جدید"
        context["submit_text"] = "ایجاد ویدیو"
        return context


class VideoUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """Dashboard view for updating an existing video with success message."""

    model = Video
    template_name = "dashboard/courses/video_form.html"
    fields = [
        "course",
        "title",
        "video_link",
        "description",
        "display_order",
        "duration",
    ]
    success_url = reverse_lazy("dashboard:courses:video-list")
    success_message = "ویدیو با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        """Add title and submit button text to the video update form context."""
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش ویدیو"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class VideoDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """Dashboard view for deleting a video with confirmation and success message."""

    model = Video
    template_name = "dashboard/courses/video_confirm_delete.html"
    success_url = reverse_lazy("dashboard:courses:video-list")
    delete_success_message = "ویدیو با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        """Add title to the video delete confirmation template context."""
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف ویدیو"
        return context


class CourseProgressListView(DashboardMixin, ListView):
    """Dashboard view for listing all course progress records with search and course filters."""

    model = CourseProgress
    template_name = "dashboard/courses/progress_list.html"
    context_object_name = "progress_items"
    paginate_by = 20
    ordering = ["-last_accessed"]

    def get_queryset(self):
        """Return optimized queryset with user and course data, filtered by search/course."""
        queryset = super().get_queryset().select_related("user", "course")
        search_query = self.request.GET.get("search", "")
        course_filter = self.request.GET.get("course", "")

        if search_query:
            queryset = queryset.filter(
                Q(user__email__icontains=search_query)
                | Q(course__title__icontains=search_query)
            )

        if course_filter:
            queryset = queryset.filter(course_id=course_filter)

        return queryset

    def get_context_data(self, **kwargs):
        """Add search query, course filter, courses list, title and create URL to context."""
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["course_filter"] = self.request.GET.get("course", "")
        context["courses"] = Course.objects.all()
        context["title"] = "مدیریت دسترسی دوره‌ها"
        context["create_url"] = reverse_lazy("dashboard:courses:progress-create")
        return context


class CourseProgressCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """Dashboard view for granting course access to a user with success message."""

    model = CourseProgress
    template_name = "dashboard/courses/progress_form.html"
    fields = ["user", "course"]
    success_url = reverse_lazy("dashboard:courses:progress-list")
    success_message = "دسترسی دوره با موفقیت برای کاربر ایجاد شد."

    def get_context_data(self, **kwargs):
        """Add title and submit button text to the progress creation form context."""
        context = super().get_context_data(**kwargs)
        context["title"] = "اعطای دسترسی به دوره"
        context["submit_text"] = "ثبت‌نام دانشجو"
        return context


class CourseProgressDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """Dashboard view for deleting course progress with confirmation and success message."""

    model = CourseProgress
    template_name = "dashboard/courses/progress_confirm_delete.html"
    success_url = reverse_lazy("dashboard:courses:progress-list")
    delete_success_message = "پیشرفت دوره با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        """Add title to the progress delete confirmation template context."""
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف پیشرفت دوره"
        return context


class CourseRatingListView(DashboardMixin, ListView):
    """Dashboard view for listing all course ratings with search, course and rating filters."""

    model = CourseRating
    template_name = "dashboard/courses/rating_list.html"
    context_object_name = "ratings"
    paginate_by = 20
    ordering = ["-created_date"]

    def get_queryset(self):
        """Return optimized queryset with user and course data, filtered by search/course/rating."""
        queryset = super().get_queryset().select_related("user", "course")
        search_query = self.request.GET.get("search", "")
        course_filter = self.request.GET.get("course", "")
        rating_filter = self.request.GET.get("rating", "")

        if search_query:
            queryset = queryset.filter(
                Q(user__email__icontains=search_query)
                | Q(course__title__icontains=search_query)
                | Q(feedback__icontains=search_query)
            )

        if course_filter:
            queryset = queryset.filter(course_id=course_filter)

        if rating_filter:
            queryset = queryset.filter(rating=rating_filter)

        return queryset

    def get_context_data(self, **kwargs):
        """Add search query, course filter, rating filter, courses list and title to context."""
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["course_filter"] = self.request.GET.get("course", "")
        context["rating_filter"] = self.request.GET.get("rating", "")
        context["courses"] = Course.objects.all()
        context["title"] = "مدیریت امتیازات دوره‌ها"
        return context


class CourseRatingUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """Dashboard view for updating a course rating with success message."""

    model = CourseRating
    template_name = "dashboard/courses/rating_form.html"
    fields = ["rating", "feedback"]
    success_url = reverse_lazy("dashboard:courses:rating-list")
    success_message = "امتیاز با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        """Add title and submit button text to the rating update form context."""
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش امتیاز"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class CourseRatingDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """Dashboard view for deleting a course rating with confirmation and success message."""

    model = CourseRating
    template_name = "dashboard/courses/rating_confirm_delete.html"
    success_url = reverse_lazy("dashboard:courses:rating-list")
    delete_success_message = "امتیاز با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        """Add title to the rating delete confirmation template context."""
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف امتیاز"
        return context
