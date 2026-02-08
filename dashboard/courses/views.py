from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from courses.models import Course, Video, CourseProgress, CourseRating
from dashboard.mixins import (
    DashboardMixin,
    SuccessMessageMixin,
    DeleteSuccessMessageMixin,
)


# ==================== Course Views ====================


class CourseListView(DashboardMixin, ListView):
    """
    نمایش لیست دوره‌ها
    """

    model = Course
    template_name = "dashboard/courses/course_list.html"
    context_object_name = "courses"
    paginate_by = 20
    ordering = ["-created_date"]

    def get_queryset(self):
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
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["title"] = "مدیریت دوره‌ها"
        context["create_url"] = reverse_lazy("dashboard:courses:course-create")
        return context


class CourseCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد دوره جدید
    """

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
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد دوره جدید"
        context["submit_text"] = "ایجاد دوره"
        return context


class CourseUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش دوره
    """

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
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش دوره"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class CourseDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    حذف دوره
    """

    model = Course
    template_name = "dashboard/courses/course_confirm_delete.html"
    success_url = reverse_lazy("dashboard:courses:course-list")
    delete_success_message = "دوره با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف دوره"
        return context


# ==================== Video Views ====================


class VideoListView(DashboardMixin, ListView):
    """
    نمایش لیست ویدیوها
    """

    model = Video
    template_name = "dashboard/courses/video_list.html"
    context_object_name = "videos"
    paginate_by = 20
    ordering = ["course", "display_order"]

    def get_queryset(self):
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
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["course_filter"] = self.request.GET.get("course", "")
        context["courses"] = Course.objects.all()
        context["title"] = "مدیریت ویدیوها"
        context["create_url"] = reverse_lazy("dashboard:courses:video-create")
        return context


class VideoCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد ویدیو جدید
    """

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
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد ویدیو جدید"
        context["submit_text"] = "ایجاد ویدیو"
        return context


class VideoUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش ویدیو
    """

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
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش ویدیو"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class VideoDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    حذف ویدیو
    """

    model = Video
    template_name = "dashboard/courses/video_confirm_delete.html"
    success_url = reverse_lazy("dashboard:courses:video-list")
    delete_success_message = "ویدیو با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف ویدیو"
        return context


# ==================== CourseProgress Views ====================


class CourseProgressListView(DashboardMixin, ListView):
    """
    نمایش لیست پیشرفت دوره‌ها
    """

    model = CourseProgress
    template_name = "dashboard/courses/progress_list.html"
    context_object_name = "progress_items"
    paginate_by = 20
    ordering = ["-last_accessed"]

    def get_queryset(self):
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
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["course_filter"] = self.request.GET.get("course", "")
        context["courses"] = Course.objects.all()
        context["title"] = "مدیریت دسترسی دوره‌ها"
        context["create_url"] = reverse_lazy("dashboard:courses:progress-create")
        return context


class CourseProgressCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """
    اعطای دسترسی جدید (ثبت‌نام دانشجو در دوره)
    """

    model = CourseProgress
    template_name = "dashboard/courses/progress_form.html"
    fields = ["user", "course"]
    success_url = reverse_lazy("dashboard:courses:progress-list")
    success_message = "دسترسی دوره با موفقیت برای کاربر ایجاد شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "اعطای دسترسی به دوره"
        context["submit_text"] = "ثبت‌نام دانشجو"
        return context


class CourseProgressDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    حذف پیشرفت دوره
    """

    model = CourseProgress
    template_name = "dashboard/courses/progress_confirm_delete.html"
    success_url = reverse_lazy("dashboard:courses:progress-list")
    delete_success_message = "پیشرفت دوره با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف پیشرفت دوره"
        return context


# ==================== CourseRating Views ====================


class CourseRatingListView(DashboardMixin, ListView):
    """
    نمایش لیست امتیازات دوره‌ها
    """

    model = CourseRating
    template_name = "dashboard/courses/rating_list.html"
    context_object_name = "ratings"
    paginate_by = 20
    ordering = ["-created_date"]

    def get_queryset(self):
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
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["course_filter"] = self.request.GET.get("course", "")
        context["rating_filter"] = self.request.GET.get("rating", "")
        context["courses"] = Course.objects.all()
        context["title"] = "مدیریت امتیازات دوره‌ها"
        return context


class CourseRatingUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش امتیاز دوره
    """

    model = CourseRating
    template_name = "dashboard/courses/rating_form.html"
    fields = ["rating", "feedback"]
    success_url = reverse_lazy("dashboard:courses:rating-list")
    success_message = "امتیاز با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش امتیاز"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class CourseRatingDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    حذف امتیاز دوره
    """

    model = CourseRating
    template_name = "dashboard/courses/rating_confirm_delete.html"
    success_url = reverse_lazy("dashboard:courses:rating-list")
    delete_success_message = "امتیاز با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف امتیاز"
        return context
