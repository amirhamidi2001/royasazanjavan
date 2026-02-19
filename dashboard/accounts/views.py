from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from accounts.models import User, Profile
from dashboard.mixins import (
    DashboardMixin,
    SuccessMessageMixin,
    DeleteSuccessMessageMixin,
)


class UserListView(DashboardMixin, ListView):
    """
    Display a paginated list of users in the dashboard.
    """

    model = User
    template_name = "dashboard/accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 20
    ordering = ["-created_date"]

    def get_queryset(self):
        """
        Return optimized queryset with optional search filtering.
        """
        queryset = super().get_queryset().select_related("user_profile")
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(email__icontains=search_query)
                | Q(user_profile__first_name__icontains=search_query)
                | Q(user_profile__last_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add search query and page title to context.
        """
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["title"] = "مدیریت کاربران"
        return context


class UserCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """
    Create a new user from the dashboard.
    """

    model = User
    template_name = "dashboard/accounts/user_form.html"
    fields = ["email", "is_staff", "is_active", "is_verified", "type"]
    success_url = reverse_lazy("dashboard:accounts:user-list")
    success_message = "کاربر با موفقیت ایجاد شد."

    def get_context_data(self, **kwargs):
        """
        Add page title and submit button text to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد کاربر جدید"
        context["submit_text"] = "ایجاد کاربر"
        return context

    def form_valid(self, form):
        """
        Set a randomly generated password before saving.
        """
        form.instance.set_password(User.objects.make_random_password())
        return super().form_valid(form)


class UserUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    Update an existing user from the dashboard.
    """

    model = User
    template_name = "dashboard/accounts/user_form.html"
    fields = ["email", "is_staff", "is_active", "is_verified", "type"]
    success_url = reverse_lazy("dashboard:accounts:user-list")
    success_message = "کاربر با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        """
        Add page title and submit button text to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش کاربر"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class UserDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    Delete a user from the dashboard.
    """

    model = User
    template_name = "dashboard/accounts/user_confirm_delete.html"
    success_url = reverse_lazy("dashboard:accounts:user-list")
    delete_success_message = "کاربر با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        """
        Add page title to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف کاربر"
        return context


class ProfileListView(DashboardMixin, ListView):
    """
    Display a paginated list of user profiles in the dashboard.
    """

    model = Profile
    template_name = "dashboard/accounts/profile_list.html"
    context_object_name = "profiles"
    paginate_by = 20
    ordering = ["-created_date"]

    def get_queryset(self):
        """
        Return optimized queryset with optional search filtering.
        """
        queryset = super().get_queryset().select_related("user")
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(user__email__icontains=search_query)
                | Q(phone_number__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add search query and page title to context.
        """
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["title"] = "مدیریت پروفایل‌ها"
        return context


class ProfileUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    Update an existing user profile from the dashboard.
    """

    model = Profile
    template_name = "dashboard/accounts/profile_form.html"
    fields = ["first_name", "last_name", "phone_number", "image"]
    success_url = reverse_lazy("dashboard:accounts:profile-list")
    success_message = "پروفایل با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        """
        Add page title and submit button text to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش پروفایل"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class ProfileDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    Delete a user profile from the dashboard.
    """

    model = Profile
    template_name = "dashboard/accounts/profile_confirm_delete.html"
    success_url = reverse_lazy("dashboard:accounts:profile-list")
    delete_success_message = "پروفایل با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        """
        Add page title to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف پروفایل"
        return context
