from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Avg

from cart.cart import CartSession
from orders.models import Order
from courses.models import Course, CourseProgress, CourseRating
from .forms import ProfileUpdateForm, EmailUpdateForm, PasswordChangeForm


@login_required
def dashboard_view(request):
    """
    Main dashboard view showing user statistics and overview.
    """
    user = request.user
    profile = user.user_profile
    cart = CartSession(request.session)

    # Get enrolled courses (purchased courses)
    enrolled_courses = user.enrolled_courses.all()[:6]  # Latest 6 courses

    # Get user orders
    orders = Order.objects.filter(user=user, is_paid=True).order_by("-created_date")[:5]

    # Calculate statistics
    total_courses = user.enrolled_courses.count()
    completed_courses = user.course_progress.filter(completion_percentage=100).count()
    in_progress_courses = user.course_progress.filter(
        completion_percentage__gt=0, completion_percentage__lt=100
    ).count()

    # Calculate total learning time
    total_learning_time = (
        sum(course.duration for course in enrolled_courses) if enrolled_courses else 0
    )

    # Get course progress data for enrolled courses
    courses_with_progress = []
    for course in enrolled_courses:
        try:
            progress = CourseProgress.objects.get(user=user, course=course)
            courses_with_progress.append({"course": course, "progress": progress})
        except CourseProgress.DoesNotExist:
            courses_with_progress.append({"course": course, "progress": None})

    context = {
        "profile": profile,
        "enrolled_courses": courses_with_progress,
        "orders": orders,
        "cart_count": cart.get_total_quantity(),
        "stats": {
            "total_courses": total_courses,
            "completed_courses": completed_courses,
            "in_progress_courses": in_progress_courses,
            "total_learning_time": total_learning_time,
        },
    }

    return render(request, "dashboard/dashboard.html", context)


@login_required
def my_courses_view(request):
    """
    Display all user's enrolled courses with filtering and search.
    """
    user = request.user

    # Get all enrolled courses
    enrolled_courses = user.enrolled_courses.all()

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        enrolled_courses = enrolled_courses.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(instructor__user_profile__first_name__icontains=search_query)
            | Q(instructor__user_profile__last_name__icontains=search_query)
        )

    # Filter by status
    status_filter = request.GET.get("status", "")
    if status_filter == "completed":
        # Get IDs of completed courses
        completed_course_ids = user.course_progress.filter(
            completion_percentage=100
        ).values_list("course_id", flat=True)
        enrolled_courses = enrolled_courses.filter(id__in=completed_course_ids)
    elif status_filter == "in_progress":
        in_progress_course_ids = user.course_progress.filter(
            completion_percentage__gt=0, completion_percentage__lt=100
        ).values_list("course_id", flat=True)
        enrolled_courses = enrolled_courses.filter(id__in=in_progress_course_ids)
    elif status_filter == "not_started":
        started_course_ids = user.course_progress.filter(
            completion_percentage__gt=0
        ).values_list("course_id", flat=True)
        enrolled_courses = enrolled_courses.exclude(id__in=started_course_ids)

    # Get progress for each course
    courses_with_progress = []
    for course in enrolled_courses:
        try:
            progress = CourseProgress.objects.get(user=user, course=course)
        except CourseProgress.DoesNotExist:
            progress = None

        courses_with_progress.append({"course": course, "progress": progress})

    context = {
        "courses_with_progress": courses_with_progress,
        "search_query": search_query,
        "status_filter": status_filter,
    }

    return render(request, "dashboard/my_courses.html", context)


@login_required
def my_orders_view(request):
    """
    Display user's order history.
    """
    orders = Order.objects.filter(user=request.user).order_by("-created_date")

    # Filter by status
    status_filter = request.GET.get("status", "")
    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        "orders": orders,
        "status_filter": status_filter,
    }

    return render(request, "dashboard/my_orders.html", context)


@login_required
def profile_settings_view(request):
    """
    View for updating profile settings.
    """
    user = request.user
    profile = user.user_profile

    if request.method == "POST":
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "پروفایل شما با موفقیت بروزرسانی شد")
            return redirect("dashboard:profile_settings")
        else:
            messages.error(request, "لطفاً خطاهای فرم را بررسی کنید")
    else:
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        "profile_form": profile_form,
        "profile": profile,
    }

    return render(request, "dashboard/profile_settings.html", context)


@login_required
def account_settings_view(request):
    """
    View for account settings including email and password change.
    """
    user = request.user

    # Handle email update
    if request.method == "POST" and "update_email" in request.POST:
        email_form = EmailUpdateForm(request.POST, instance=user)
        if email_form.is_valid():
            email_form.save()
            messages.success(request, "ایمیل شما با موفقیت بروزرسانی شد")
            return redirect("dashboard:account_settings")
    else:
        email_form = EmailUpdateForm(instance=user)

    # Handle password change
    if request.method == "POST" and "change_password" in request.POST:
        password_form = PasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            password_form.save()
            # Keep user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, "رمز عبور شما با موفقیت تغییر کرد")
            return redirect("dashboard:account_settings")
    else:
        password_form = PasswordChangeForm(user)

    context = {
        "email_form": email_form,
        "password_form": password_form,
    }

    return render(request, "dashboard/account_settings.html", context)


@login_required
def my_reviews_view(request):
    """
    Display user's course reviews.
    """
    reviews = CourseRating.objects.filter(user=request.user).select_related("course")

    context = {
        "reviews": reviews,
    }

    return render(request, "dashboard/my_reviews.html", context)


@login_required
@require_POST
def delete_review_view(request, review_id):
    """
    Delete a course review.
    """
    review = get_object_or_404(CourseRating, id=review_id, user=request.user)
    course_title = review.course.title
    review.delete()

    messages.success(request, f'نظر شما در مورد دوره "{course_title}" حذف شد')
    return redirect("dashboard:my_reviews")


@login_required
def statistics_view(request):
    """
    Display detailed user statistics and analytics.
    """
    user = request.user

    # Course statistics
    total_courses = user.enrolled_courses.count()
    completed_courses = user.course_progress.filter(completion_percentage=100).count()
    in_progress_courses = user.course_progress.filter(
        completion_percentage__gt=0, completion_percentage__lt=100
    ).count()
    not_started = total_courses - (completed_courses + in_progress_courses)

    # Learning time statistics
    total_duration = (
        user.enrolled_courses.aggregate(total=Count("duration"))["total"] or 0
    )

    # Video watching statistics
    total_videos_watched = sum(
        progress.watched_videos.count() for progress in user.course_progress.all()
    )

    # Order statistics
    total_spent = sum(
        order.final_price for order in Order.objects.filter(user=user, is_paid=True)
    )

    # Average rating given
    avg_rating = (
        CourseRating.objects.filter(user=user).aggregate(avg=Avg("rating"))["avg"] or 0
    )

    context = {
        "course_stats": {
            "total": total_courses,
            "completed": completed_courses,
            "in_progress": in_progress_courses,
            "not_started": not_started,
        },
        "learning_stats": {
            "total_duration": total_duration,
            "videos_watched": total_videos_watched,
        },
        "financial_stats": {
            "total_spent": total_spent,
        },
        "engagement_stats": {
            "avg_rating": round(avg_rating, 1),
            "reviews_count": CourseRating.objects.filter(user=user).count(),
        },
    }

    return render(request, "dashboard/statistics.html", context)


@login_required
@require_POST
def upload_profile_image_ajax(request):
    """
    AJAX endpoint for uploading profile image.
    """
    if "image" not in request.FILES:
        return JsonResponse({"success": False, "message": "تصویری انتخاب نشده است"})

    profile = request.user.user_profile
    image = request.FILES["image"]

    # Validate image
    if image.size > 2 * 1024 * 1024:  # 2MB
        return JsonResponse(
            {"success": False, "message": "حجم تصویر نباید بیشتر از 2 مگابایت باشد"}
        )

    # Save image
    profile.image = image
    profile.save()

    return JsonResponse(
        {
            "success": True,
            "message": "تصویر پروفایل با موفقیت بروزرسانی شد",
            "image_url": profile.image.url,
        }
    )
