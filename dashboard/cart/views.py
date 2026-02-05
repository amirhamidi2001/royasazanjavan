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


# ==================== Cart Views ====================


class CartListView(DashboardMixin, ListView):
    """
    نمایش لیست سبدهای خرید
    """

    model = CartModel
    template_name = "dashboard/cart/cart_list.html"
    context_object_name = "carts"
    paginate_by = 20
    ordering = ["-updated_date"]

    def get_queryset(self):
        queryset = (
            super().get_queryset().select_related("user").prefetch_related("items")
        )
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(user__email__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["title"] = "مدیریت سبدهای خرید"
        return context


class CartDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    حذف سبد خرید
    """

    model = CartModel
    template_name = "dashboard/cart/cart_confirm_delete.html"
    success_url = reverse_lazy("dashboard:cart:cart-list")
    delete_success_message = "سبد خرید با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف سبد خرید"
        return context
