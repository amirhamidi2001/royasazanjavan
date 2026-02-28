from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from files.models import ExcelFile
from dashboard.mixins import (
    DashboardMixin,
    SuccessMessageMixin,
    DeleteSuccessMessageMixin,
)


class ExcelFileListView(DashboardMixin, ListView):
    """
    Displays a paginated list of ExcelFile objects.
    """

    model = ExcelFile
    template_name = "dashboard/files/excelfile_list.html"
    context_object_name = "files"
    paginate_by = 20
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["title"] = "مدیریت فایل‌های اکسل"
        context["create_url"] = reverse_lazy("dashboard:files:excelfile-create")
        return context


class ExcelFileCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """
    Adds success message after successful creation.
    """

    model = ExcelFile
    fields = ["title", "description", "file"]
    template_name = "dashboard/files/excelfile_form.html"
    success_url = reverse_lazy("dashboard:files:excelfile-list")
    success_message = "فایل اکسل با موفقیت ایجاد شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد فایل اکسل"
        context["submit_text"] = "ایجاد"
        return context


class ExcelFileUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    Handles editing existing records.
    """

    model = ExcelFile
    fields = ["title", "description", "file"]
    template_name = "dashboard/files/excelfile_form.html"
    success_url = reverse_lazy("dashboard:files:excelfile-list")
    success_message = "فایل اکسل با موفقیت بروزرسانی شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش فایل اکسل"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class ExcelFileDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    Uses custom delete success mixin.
    """

    model = ExcelFile
    template_name = "dashboard/files/excelfile_confirm_delete.html"
    success_url = reverse_lazy("dashboard:files:excelfile-list")
    delete_success_message = "فایل اکسل با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف فایل اکسل"
        return context
