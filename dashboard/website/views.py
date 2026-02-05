from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from cart.models import CartModel, CartItemModel
from orders.models import Order, OrderItem, Coupon
from website.models import ConsultationRequest, Contact, JobApplication, Newsletter
from dashboard.mixins import (
    DashboardMixin,
    SuccessMessageMixin,
    DeleteSuccessMessageMixin,
)


# ==================== Website Views ====================


class ConsultationRequestListView(DashboardMixin, ListView):
    """
    نمایش لیست درخواست‌های مشاوره
    """

    model = ConsultationRequest
    template_name = "dashboard/website/consultation_list.html"
    context_object_name = "consultations"
    paginate_by = 20
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")
        type_filter = self.request.GET.get("type", "")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(subject__icontains=search_query)
            )

        if type_filter:
            queryset = queryset.filter(consultation_type=type_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["type_filter"] = self.request.GET.get("type", "")
        context["title"] = "مدیریت درخواست‌های مشاوره"
        return context


class ConsultationRequestDeleteView(
    DashboardMixin, DeleteSuccessMessageMixin, DeleteView
):
    """
    حذف درخواست مشاوره
    """

    model = ConsultationRequest
    template_name = "dashboard/website/consultation_confirm_delete.html"
    success_url = reverse_lazy("dashboard:website:consultation-list")
    delete_success_message = "درخواست مشاوره با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف درخواست مشاوره"
        return context


class ContactListView(DashboardMixin, ListView):
    """
    نمایش لیست تماس‌ها
    """

    model = Contact
    template_name = "dashboard/website/contact_list.html"
    context_object_name = "contacts"
    paginate_by = 20
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(subject__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["title"] = "مدیریت تماس‌ها"
        return context


class ContactDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    حذف تماس
    """

    model = Contact
    template_name = "dashboard/website/contact_confirm_delete.html"
    success_url = reverse_lazy("dashboard:website:contact-list")
    delete_success_message = "تماس با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف تماس"
        return context


class JobApplicationListView(DashboardMixin, ListView):
    """
    نمایش لیست درخواست‌های شغلی
    """

    model = JobApplication
    template_name = "dashboard/website/job_list.html"
    context_object_name = "applications"
    paginate_by = 20
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(subject__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["title"] = "مدیریت درخواست‌های شغلی"
        return context


class JobApplicationDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    حذف درخواست شغلی
    """

    model = JobApplication
    template_name = "dashboard/website/job_confirm_delete.html"
    success_url = reverse_lazy("dashboard:website:job-list")
    delete_success_message = "درخواست شغلی با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف درخواست شغلی"
        return context


class NewsletterListView(DashboardMixin, ListView):
    """
    نمایش لیست مشترکین خبرنامه
    """

    model = Newsletter
    template_name = "dashboard/website/newsletter_list.html"
    context_object_name = "newsletters"
    paginate_by = 20
    ordering = ["email"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(email__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["title"] = "مدیریت مشترکین خبرنامه"
        return context


class NewsletterDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    حذف مشترک خبرنامه
    """

    model = Newsletter
    template_name = "dashboard/website/newsletter_confirm_delete.html"
    success_url = reverse_lazy("dashboard:website:newsletter-list")
    delete_success_message = "مشترک خبرنامه با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف مشترک خبرنامه"
        return context
