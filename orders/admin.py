from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem, Coupon, OrderStatusChoices


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items with Generic FK support"""

    model = OrderItem
    extra = 0
    readonly_fields = (
        "get_product_info",
        "get_product_type",
        "price",
        "quantity",
        "get_total_price_display",
        "created_date",
    )
    fields = (
        "get_product_type",
        "get_product_info",
        "price",
        "quantity",
        "get_total_price_display",
    )
    can_delete = False

    def get_product_info(self, obj):
        if not obj.content_object:
            return "محصول حذف شده"

        product = obj.content_object
        product_type = obj.content_type.model

        if product_type == "course":
            url = reverse("admin:courses_course_change", args=[product.id])
        elif product_type == "product":
            url = reverse("admin:shop_product_change", args=[product.id])
        else:
            return product.title

        return format_html('<a href="{}" target="_blank">{}</a>', url, product.title)

    get_product_info.short_description = "محصول"

    def get_product_type(self, obj):
        product_type = obj.content_type.model
        badges = {
            "course": '<span style="background: #007bff; color: white; padding: 3px 8px; border-radius: 3px;">دوره</span>',
            "product": '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">محصول</span>',
        }
        return mark_safe(badges.get(product_type, product_type))

    get_product_type.short_description = "نوع"

    def get_total_price_display(self, obj):
        return f"{obj.get_total_price():,} تومان"

    get_total_price_display.short_description = "قیمت کل"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "get_user_email",
        "get_full_name",
        "final_price_display",
        "get_status_badge",
        "is_paid",
        "created_date",
    )
    list_filter = (
        "status",
        "is_paid",
        "created_date",
        "payment_date",
    )
    search_fields = (
        "order_number",
        "user__email",
        "user__first_name",
        "user__last_name",
        "first_name",
        "last_name",
        "email",
        "phone",
        "zarinpal_ref_id",
    )
    readonly_fields = (
        "order_number",
        "created_date",
        "updated_date",
        "payment_date",
        "get_total_items",
        "final_price_display",
    )
    inlines = [OrderItemInline]

    fieldsets = (
        (
            "اطلاعات سفارش",
            {
                "fields": (
                    "order_number",
                    "user",
                    "status",
                    "get_total_items",
                )
            },
        ),
        (
            "اطلاعات مشتری",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                )
            },
        ),
        (
            "آدرس",
            {
                "fields": (
                    "address",
                    "apartment",
                    "city",
                    "state",
                    "zip_code",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "اطلاعات مالی",
            {
                "fields": (
                    "total_price",
                    "discount_amount",
                    "tax_amount",
                    "final_price_display",
                )
            },
        ),
        (
            "اطلاعات پرداخت",
            {
                "fields": (
                    "is_paid",
                    "zarinpal_authority",
                    "zarinpal_ref_id",
                    "payment_date",
                )
            },
        ),
        (
            "سایر",
            {
                "fields": (
                    "notes",
                    "created_date",
                    "updated_date",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def get_user_email(self, obj):
        return obj.user.email

    get_user_email.short_description = "کاربر"
    get_user_email.admin_order_field = "user__email"

    def get_status_badge(self, obj):
        colors = {
            OrderStatusChoices.PENDING: "#ffc107",
            OrderStatusChoices.PROCESSING: "#17a2b8",
            OrderStatusChoices.PAID: "#28a745",
            OrderStatusChoices.FAILED: "#dc3545",
            OrderStatusChoices.CANCELLED: "#6c757d",
            OrderStatusChoices.REFUNDED: "#e83e8c",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    get_status_badge.short_description = "وضعیت"
    get_status_badge.admin_order_field = "status"

    def final_price_display(self, obj):
        return f"{obj.final_price:,} تومان"

    final_price_display.short_description = "مبلغ نهایی"
    final_price_display.admin_order_field = "final_price"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user").prefetch_related("items")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_order_number",
        "get_product_type",
        "get_product_name",
        "price_display",
        "quantity",
        "get_total_price_display",
        "created_date",
    )
    list_filter = (
        "content_type",
        "created_date",
    )
    search_fields = (
        "order__order_number",
        "order__user__email",
    )
    readonly_fields = (
        "order",
        "content_type",
        "object_id",
        "get_product_info",
        "price",
        "quantity",
        "get_total_price_display",
        "created_date",
    )

    fieldsets = (
        ("سفارش", {"fields": ("order",)}),
        ("محصول", {"fields": ("content_type", "object_id", "get_product_info")}),
        (
            "قیمت",
            {
                "fields": (
                    "price",
                    "quantity",
                    "get_total_price_display",
                    "created_date",
                )
            },
        ),
    )

    def get_order_number(self, obj):
        url = reverse("admin:orders_order_change", args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)

    get_order_number.short_description = "سفارش"
    get_order_number.admin_order_field = "order__order_number"

    def get_product_type(self, obj):
        product_type = obj.content_type.model
        badges = {
            "course": '<span style="background: #007bff; color: white; padding: 3px 8px; border-radius: 3px;">دوره</span>',
            "product": '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">محصول</span>',
        }
        return mark_safe(badges.get(product_type, product_type))

    get_product_type.short_description = "نوع"

    def get_product_name(self, obj):
        return obj.get_product_name()

    get_product_name.short_description = "محصول"

    def get_product_info(self, obj):
        if not obj.content_object:
            return "محصول موجود نیست"

        product = obj.content_object
        info = f"نام: {product.title}<br>"
        info += f"نوع: {obj.content_type.model}<br>"

        if obj.content_type.model == "course":
            info += f"مدرس: {getattr(product.instructor, 'email', 'Unknown')}<br>"
            info += f"قیمت: {product.price:,} تومان"
        elif obj.content_type.model == "product":
            final_price = product.get_final_price()
            info += f"قیمت نهایی: {final_price:,} تومان<br>"
            if product.is_discounted():
                info += f"<span style='color: red;'>تخفیف: {product.get_discount_percentage()}%</span>"

        return mark_safe(info)

    get_product_info.short_description = "اطلاعات محصول"

    def price_display(self, obj):
        return f"{obj.price:,} تومان"

    price_display.short_description = "قیمت واحد"

    def get_total_price_display(self, obj):
        return f"{obj.get_total_price():,} تومان"

    get_total_price_display.short_description = "قیمت کل"

    def has_add_permission(self, request):
        return False


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "get_discount_display",
        "get_usage_display",
        "min_purchase_amount",
        "get_active_badge",
        "valid_from",
        "valid_to",
    )
    list_filter = (
        "is_active",
        "valid_from",
        "valid_to",
    )
    search_fields = ("code",)
    readonly_fields = (
        "current_usage",
        "created_date",
        "updated_date",
    )

    fieldsets = (
        ("اطلاعات کد تخفیف", {"fields": ("code", "is_active")}),
        (
            "تخفیف",
            {
                "fields": (
                    "discount_percentage",
                    "discount_amount",
                    "min_purchase_amount",
                ),
                "description": "یکی از دو فیلد درصد یا مبلغ را پر کنید",
            },
        ),
        (
            "محدودیت‌ها",
            {
                "fields": (
                    "max_usage",
                    "current_usage",
                    "valid_from",
                    "valid_to",
                )
            },
        ),
        (
            "تاریخ‌ها",
            {"fields": ("created_date", "updated_date"), "classes": ("collapse",)},
        ),
    )

    def get_discount_display(self, obj):
        if obj.discount_amount > 0:
            return f"{obj.discount_amount:,} تومان"
        elif obj.discount_percentage > 0:
            return f"{obj.discount_percentage}%"
        return "-"

    get_discount_display.short_description = "تخفیف"

    def get_usage_display(self, obj):
        percentage = (
            (obj.current_usage / obj.max_usage * 100) if obj.max_usage > 0 else 0
        )
        color = (
            "#28a745"
            if percentage < 80
            else "#ffc107" if percentage < 100 else "#dc3545"
        )
        return format_html(
            '<span style="color: {};">{} / {}</span>',
            color,
            obj.current_usage,
            obj.max_usage,
        )

    get_usage_display.short_description = "استفاده شده"

    def get_active_badge(self, obj):
        if obj.is_valid():
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">فعال</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">غیرفعال</span>'
            )

    get_active_badge.short_description = "وضعیت"
