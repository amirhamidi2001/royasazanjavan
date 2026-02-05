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
    نمایش لیست کاربران
    """

    model = User
    template_name = "dashboard/accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 20
    ordering = ["-created_date"]

    def get_queryset(self):
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
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["title"] = "مدیریت کاربران"
        return context


class UserCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد کاربر جدید
    """

    model = User
    template_name = "dashboard/accounts/user_form.html"
    fields = ["email", "is_staff", "is_active", "is_verified", "type"]
    success_url = reverse_lazy("dashboard:accounts:user-list")
    success_message = "کاربر با موفقیت ایجاد شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد کاربر جدید"
        context["submit_text"] = "ایجاد کاربر"
        return context

    def form_valid(self, form):
        form.instance.set_password(User.objects.make_random_password())
        return super().form_valid(form)


class UserUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش کاربر
    """

    model = User
    template_name = "dashboard/accounts/user_form.html"
    fields = ["email", "is_staff", "is_active", "is_verified", "type"]
    success_url = reverse_lazy("dashboard:accounts:user-list")
    success_message = "کاربر با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش کاربر"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class UserDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    حذف کاربر
    """

    model = User
    template_name = "dashboard/accounts/user_confirm_delete.html"
    success_url = reverse_lazy("dashboard:accounts:user-list")
    delete_success_message = "کاربر با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف کاربر"
        return context


# ==================== Profile Views ====================


class ProfileListView(DashboardMixin, ListView):
    """
    نمایش لیست پروفایل‌ها
    """

    model = Profile
    template_name = "dashboard/accounts/profile_list.html"
    context_object_name = "profiles"
    paginate_by = 20
    ordering = ["-created_date"]

    def get_queryset(self):
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
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["title"] = "مدیریت پروفایل‌ها"
        return context


class ProfileUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش پروفایل
    """

    model = Profile
    template_name = "dashboard/accounts/profile_form.html"
    fields = ["first_name", "last_name", "phone_number", "image"]
    success_url = reverse_lazy("dashboard:accounts:profile-list")
    success_message = "پروفایل با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش پروفایل"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class ProfileDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    حذف پروفایل
    """

    model = Profile
    template_name = "dashboard/accounts/profile_confirm_delete.html"
    success_url = reverse_lazy("dashboard:accounts:profile-list")
    delete_success_message = "پروفایل با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف پروفایل"
        return context
