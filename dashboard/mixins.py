from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin برای محدود کردن دسترسی به کاربران Staff
    """

    login_url = reverse_lazy("accounts:login")
    permission_denied_message = "شما دسترسی به این بخش را ندارید."

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return redirect(self.login_url)


class SuccessMessageMixin:
    """
    Mixin برای نمایش پیام موفقیت پس از عملیات
    """

    success_message = ""

    def get_success_message(self):
        return self.success_message

    def form_valid(self, form):
        response = super().form_valid(form)
        success_message = self.get_success_message()
        if success_message:
            messages.success(self.request, success_message)
        return response


class DeleteSuccessMessageMixin:
    """
    Mixin برای نمایش پیام موفقیت پس از حذف
    """

    delete_success_message = ""

    def get_delete_success_message(self):
        return self.delete_success_message

    def delete(self, request, *args, **kwargs):
        delete_message = self.get_delete_success_message()
        if delete_message:
            messages.success(request, delete_message)
        return super().delete(request, *args, **kwargs)


class DashboardMixin(StaffRequiredMixin):
    """
    Mixin پایه برای تمام ویوهای داشبورد
    """

    pass
