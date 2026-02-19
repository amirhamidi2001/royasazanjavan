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


class OrderListView(DashboardMixin, ListView):
    """
    Displays a paginated list of orders in the dashboard.
    """

    model = Order
    template_name = "dashboard/orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 20
    ordering = ["-created_date"]

    def get_queryset(self):
        """
        Returns filtered queryset:
        """
        queryset = (
            super().get_queryset().select_related("user").prefetch_related("items")
        )
        search_query = self.request.GET.get("search", "")
        status_filter = self.request.GET.get("status", "")

        if search_query:
            queryset = queryset.filter(
                Q(order_number__icontains=search_query)
                | Q(user__email__icontains=search_query)
                | Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
            )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds search values, status filter, and page title to context.
        """
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["title"] = "مدیریت سفارشات"
        return context


class OrderUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    Handles updating an existing order.
    """

    model = Order
    template_name = "dashboard/orders/order_form.html"
    fields = ["status", "notes"]
    success_url = reverse_lazy("dashboard:orders:order-list")
    success_message = "سفارش با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        """
        Adds page title and submit button text.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش سفارش"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class OrderDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    Handles deletion of an order.
    """

    model = Order
    template_name = "dashboard/orders/order_confirm_delete.html"
    success_url = reverse_lazy("dashboard:orders:order-list")
    delete_success_message = "سفارش با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        """
        Adds page title to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف سفارش"
        return context


class CouponListView(DashboardMixin, ListView):
    """
    Displays a paginated list of discount coupons.
    """

    model = Coupon
    template_name = "dashboard/orders/coupon_list.html"
    context_object_name = "coupons"
    paginate_by = 20
    ordering = ["-created_date"]

    def get_queryset(self):
        """
        Returns filtered queryset:
        """
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")
        status_filter = self.request.GET.get("status", "")

        if search_query:
            queryset = queryset.filter(code__icontains=search_query)

        if status_filter == "active":
            queryset = queryset.filter(is_active=True)
        elif status_filter == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds search values, status filter,
        and page title to context.
        """
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["title"] = "مدیریت کدهای تخفیف"
        return context


class CouponCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """
    Handles creation of a new coupon.
    """

    model = Coupon
    template_name = "dashboard/orders/coupon_form.html"
    fields = [
        "code",
        "discount_percentage",
        "discount_amount",
        "max_usage",
        "min_purchase_amount",
        "is_active",
        "valid_from",
        "valid_to",
    ]
    success_url = reverse_lazy("dashboard:orders:coupon-list")
    success_message = "کد تخفیف با موفقیت ایجاد شد."

    def get_context_data(self, **kwargs):
        """
        Adds page title and submit button text.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد کد تخفیف جدید"
        context["submit_text"] = "ایجاد کد تخفیف"
        return context


class CouponUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    Handles updating an existing coupon.
    """

    model = Coupon
    template_name = "dashboard/orders/coupon_form.html"
    fields = [
        "code",
        "discount_percentage",
        "discount_amount",
        "max_usage",
        "min_purchase_amount",
        "is_active",
        "valid_from",
        "valid_to",
    ]
    success_url = reverse_lazy("dashboard:orders:coupon-list")
    success_message = "کد تخفیف با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        """
        Adds page title and submit button text.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش کد تخفیف"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class CouponDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    Handles deletion of a coupon.
    """

    model = Coupon
    template_name = "dashboard/orders/coupon_confirm_delete.html"
    success_url = reverse_lazy("dashboard:orders:coupon-list")
    delete_success_message = "کد تخفیف با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        """
        Adds page title to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف کد تخفیف"
        return context
