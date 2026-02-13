from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum
from shop.models import Category, Product, ProductFeature
from dashboard.mixins import (
    DashboardMixin,
    SuccessMessageMixin,
    DeleteSuccessMessageMixin,
)


# ==================== Category Views ====================


class CategoryListView(DashboardMixin, ListView):
    """
    نمایش لیست دسته‌بندی‌های محصولات
    """

    model = Category
    template_name = "dashboard/shop/category_list.html"
    context_object_name = "categories"
    paginate_by = 20
    ordering = ["name"]

    def get_queryset(self):
        queryset = super().get_queryset().annotate(products_count=Count("products"))
        search_query = self.request.GET.get("search", "")
        status_filter = self.request.GET.get("status", "")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
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
        context["title"] = "مدیریت دسته‌بندی‌های محصولات"
        context["create_url"] = reverse_lazy("dashboard:shop:category-create")
        return context


class CategoryCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد دسته‌بندی جدید
    """

    model = Category
    template_name = "dashboard/shop/category_form.html"
    fields = ["name", "slug", "parent", "description", "is_active"]
    success_url = reverse_lazy("dashboard:shop:category-list")
    success_message = "دسته‌بندی با موفقیت ایجاد شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد دسته‌بندی جدید"
        context["submit_text"] = "ایجاد دسته‌بندی"
        return context


class CategoryUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش دسته‌بندی
    """

    model = Category
    template_name = "dashboard/shop/category_form.html"
    fields = ["name", "slug", "parent", "description", "is_active"]
    success_url = reverse_lazy("dashboard:shop:category-list")
    success_message = "دسته‌بندی با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش دسته‌بندی"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class CategoryDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    حذف دسته‌بندی
    """

    model = Category
    template_name = "dashboard/shop/category_confirm_delete.html"
    success_url = reverse_lazy("dashboard:shop:category-list")
    delete_success_message = "دسته‌بندی با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف دسته‌بندی"
        return context


# ==================== Product Views ====================


class ProductListView(DashboardMixin, ListView):
    """
    نمایش لیست محصولات
    """

    model = Product
    template_name = "dashboard/shop/product_list.html"
    context_object_name = "products"
    paginate_by = 20
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset().select_related("category")
        search_query = self.request.GET.get("search", "")
        status_filter = self.request.GET.get("status", "")
        type_filter = self.request.GET.get("type", "")
        category_filter = self.request.GET.get("category", "")

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(short_description__icontains=search_query)
            )

        if status_filter == "active":
            queryset = queryset.filter(is_active=True)
        elif status_filter == "inactive":
            queryset = queryset.filter(is_active=False)

        if type_filter:
            queryset = queryset.filter(product_type=type_filter)

        if category_filter:
            queryset = queryset.filter(category_id=category_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["type_filter"] = self.request.GET.get("type", "")
        context["category_filter"] = self.request.GET.get("category", "")
        context["categories"] = Category.objects.filter(is_active=True)
        context["title"] = "مدیریت محصولات"
        context["create_url"] = reverse_lazy("dashboard:shop:product-create")
        return context


class ProductCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد محصول جدید
    """

    model = Product
    template_name = "dashboard/shop/product_form.html"
    fields = [
        "title",
        "slug",
        "category",
        "product_type",
        "description",
        "short_description",
        "price",
        "discounted_price",
        "is_free",
        "stock",
        "image",
        "is_active",
        "is_featured",
    ]
    success_url = reverse_lazy("dashboard:shop:product-list")
    success_message = "محصول با موفقیت ایجاد شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد محصول جدید"
        context["submit_text"] = "ایجاد محصول"
        return context


class ProductUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش محصول
    """

    model = Product
    template_name = "dashboard/shop/product_form.html"
    fields = [
        "title",
        "slug",
        "category",
        "product_type",
        "description",
        "short_description",
        "price",
        "discounted_price",
        "is_free",
        "stock",
        "image",
        "is_active",
        "is_featured",
    ]
    success_url = reverse_lazy("dashboard:shop:product-list")
    success_message = "محصول با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش محصول"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class ProductDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    حذف محصول
    """

    model = Product
    template_name = "dashboard/shop/product_confirm_delete.html"
    success_url = reverse_lazy("dashboard:shop:product-list")
    delete_success_message = "محصول با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف محصول"
        return context


# ==================== ProductFeature Views ====================


class ProductFeatureListView(DashboardMixin, ListView):
    """
    نمایش لیست ویژگی‌های محصولات
    """

    model = ProductFeature
    template_name = "dashboard/shop/feature_list.html"
    context_object_name = "features"
    paginate_by = 20
    ordering = ["product", "order"]

    def get_queryset(self):
        queryset = super().get_queryset().select_related("product")
        search_query = self.request.GET.get("search", "")
        product_filter = self.request.GET.get("product", "")

        if search_query:
            queryset = queryset.filter(
                Q(feature_name__icontains=search_query)
                | Q(feature_value__icontains=search_query)
                | Q(product__title__icontains=search_query)
            )

        if product_filter:
            queryset = queryset.filter(product_id=product_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["product_filter"] = self.request.GET.get("product", "")
        context["products"] = Product.objects.filter(is_active=True)
        context["title"] = "مدیریت ویژگی‌های محصولات"
        context["create_url"] = reverse_lazy("dashboard:shop:feature-create")
        return context


class ProductFeatureCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """
    ایجاد ویژگی محصول جدید
    """

    model = ProductFeature
    template_name = "dashboard/shop/feature_form.html"
    fields = ["product", "feature_name", "feature_value", "order"]
    success_url = reverse_lazy("dashboard:shop:feature-list")
    success_message = "ویژگی محصول با موفقیت ایجاد شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد ویژگی محصول"
        context["submit_text"] = "ایجاد ویژگی"
        return context


class ProductFeatureUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    ویرایش ویژگی محصول
    """

    model = ProductFeature
    template_name = "dashboard/shop/feature_form.html"
    fields = ["product", "feature_name", "feature_value", "order"]
    success_url = reverse_lazy("dashboard:shop:feature-list")
    success_message = "ویژگی محصول با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش ویژگی محصول"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class ProductFeatureDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    حذف ویژگی محصول
    """

    model = ProductFeature
    template_name = "dashboard/shop/feature_confirm_delete.html"
    success_url = reverse_lazy("dashboard:shop:feature-list")
    delete_success_message = "ویژگی محصول با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف ویژگی محصول"
        return context
