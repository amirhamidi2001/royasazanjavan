from django.core.paginator import EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Count

from courses.models import Course, Video, CourseProgress, CourseRating
from courses.forms import CourseRatingForm


class CourseListView(ListView):
    """Display a list of all active courses."""

    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"
    paginate_by = 12

    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True).annotate(
            avg_rating=Avg("ratings__rating"),
            total_students=Count("students", distinct=True),
        )
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset

    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1

        try:
            page_number = int(page)
            page_obj = paginator.page(page_number)
        except (PageNotAnInteger, ValueError):
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return (paginator, page_obj, page_obj.object_list, page_obj.has_other_pages())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        return context


class CourseDetailView(LoginRequiredMixin, DetailView):
    """ """

    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        """ """
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        progress = CourseProgress.objects.filter(user=user, course=course).first()

        is_enrolled = progress is not None

        videos = course.videos.all().order_by("display_order")

        try:
            user_rating = CourseRating.objects.get(user=user, course=course)
        except CourseRating.DoesNotExist:
            user_rating = None

        rating_form = CourseRatingForm(instance=user_rating)

        ratings = course.ratings.select_related("user").order_by("-created_date")

        context.update(
            {
                "videos": videos,
                "progress": progress,
                "is_enrolled": is_enrolled,
                "ratings": ratings,
                "rating_form": rating_form,
                "user_rating": user_rating,
                "avg_rating": course.get_average_rating(),
            }
        )
        return context


class SubmitRatingView(LoginRequiredMixin, View):
    """Handle the submission of a course rating."""

    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug, is_active=True)
        user = request.user

        # Check enrollment
        if not CourseProgress.objects.filter(user=user, course=course).exists():
            messages.error(request, _("You must be enrolled in the course to rate it."))
            return redirect("courses:course_detail", slug=slug)

        try:
            existing_rating = CourseRating.objects.get(user=user, course=course)
            form = CourseRatingForm(request.POST, instance=existing_rating)
            is_update = True
        except CourseRating.DoesNotExist:
            form = CourseRatingForm(request.POST)
            is_update = False

        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = user
            rating.course = course
            rating.save()
            if is_update:
                messages.success(
                    request, _("Your rating has been updated successfully.")
                )
            else:
                messages.success(request, _("Thank you for rating this course!"))
        else:
            messages.error(request, _("Please correct the errors below."))

        return redirect("courses:course_detail", slug=slug)


class CourseProgressView(LoginRequiredMixin, ListView):
    """Display user's progress across all enrolled courses."""

    model = CourseProgress
    template_name = "courses/course_progress.html"
    context_object_name = "progress_list"

    def get_queryset(self):
        return (
            CourseProgress.objects.filter(user=self.request.user)
            .select_related("course")
            .prefetch_related("watched_videos")
            .order_by("-last_accessed")
        )


# class MarkVideoWatchedView(LoginRequiredMixin, View):
#     """Mark a video as watched and update user's progress."""

#     def post(self, request, slug, video_id):
#         course = get_object_or_404(Course, slug=slug, is_active=True)
#         video = get_object_or_404(Video, id=video_id, course=course)

#         progress, _ = CourseProgress.objects.get_or_create(
#             user=request.user, course=course
#         )
#         progress.mark_video_watched(video)


#         messages.success(
#             request,
#             _("Video '%(video_title)s' marked as watched.")
#             % {"video_title": video.title},
#         )
#         return redirect("courses:course_detail", slug=slug)
class MarkVideoWatchedView(LoginRequiredMixin, View):
    def post(self, request, slug, video_id):
        course = get_object_or_404(Course, slug=slug, is_active=True)
        video = get_object_or_404(Video, id=video_id, course=course)

        progress, created = CourseProgress.objects.get_or_create(
            user=request.user, course=course
        )

        progress.mark_video_watched(video)

        messages.success(
            request,
            _("Video '%(video_title)s' marked as watched.")
            % {"video_title": video.title},
        )

        return redirect("courses:course_detail", slug=slug)


class EnrollCourseView(LoginRequiredMixin, View):
    """Enroll user in a course."""

    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug, is_active=True)

        if CourseProgress.objects.filter(user=request.user, course=course).exists():
            messages.info(request, _("You are already enrolled in this course."))
        else:
            CourseProgress.objects.create(user=request.user, course=course)
            messages.success(
                request,
                _("You have successfully enrolled in %(course_title)s!")
                % {"course_title": course.title},
            )

        return redirect("courses:course_detail", slug=slug)
