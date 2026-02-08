from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Coupon


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""

    model = OrderItem
    extra = 0
    readonly_fields = ("get_total_price",)
    fields = ("course", "price", "quantity", "get_total_price")
    raw_id_fields = ("course",)

    def get_total_price(self, obj):
        if obj.id:
            return f"{obj.get_total_price():,} تومان"
        return "-"

    get_total_price.short_description = "قیمت کل"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order model."""

    list_display = (
        "order_number",
        "user",
        "get_full_name",
        "email",
        "final_price",
        "status_badge",
        "is_paid",
        "created_date",
    )
    list_filter = ("is_paid", "status", "created_date", "payment_date")
    search_fields = (
        "order_number",
        "user__email",
        "email",
        "first_name",
        "last_name",
        "phone",
        "zarinpal_authority",
        "zarinpal_ref_id",
    )
    readonly_fields = (
        "order_number",
        "created_date",
        "updated_date",
        "payment_date",
        "get_total_items",
    )

    fieldsets = (
        (
            "اطلاعات سفارش",
            {
                "fields": (
                    "order_number",
                    "user",
                    "status",
                    "created_date",
                    "updated_date",
                )
            },
        ),
        ("اطلاعات خریدار", {"fields": ("first_name", "last_name", "email", "phone")}),
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
            {"fields": ("total_price", "discount_amount", "tax_amount", "final_price")},
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
        ("سایر", {"fields": ("notes",), "classes": ("collapse",)}),
    )

    inlines = [OrderItemInline]

    def status_badge(self, obj):
        """Display colored status badge."""
        colors = {
            "pending": "orange",
            "processing": "blue",
            "paid": "green",
            "failed": "red",
            "cancelled": "gray",
            "refunded": "purple",
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "وضعیت"

    def get_total_items(self, obj):
        return obj.get_total_items()

    get_total_items.short_description = "تعداد آیتم‌ها"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for OrderItem model."""

    list_display = (
        "order",
        "course",
        "price",
        "quantity",
        "get_total_price_display",
        "created_date",
    )
    list_filter = ("created_date",)
    search_fields = ("order__order_number", "course__title", "order__user__email")
    readonly_fields = ("created_date", "get_total_price")
    raw_id_fields = ("order", "course")

    def get_total_price_display(self, obj):
        return f"{obj.get_total_price():,} تومان"

    get_total_price_display.short_description = "قیمت کل"


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin interface for Coupon model."""

    list_display = (
        "code",
        "discount_display",
        "usage_display",
        "validity_display",
        "is_active",
        "created_date",
    )
    list_filter = ("is_active", "created_date", "valid_from", "valid_to")
    search_fields = ("code",)
    readonly_fields = ("current_usage", "created_date", "updated_date")

    fieldsets = (
        ("اطلاعات کد تخفیف", {"fields": ("code", "is_active")}),
        (
            "تخفیف",
            {
                "fields": (
                    "discount_percentage",
                    "discount_amount",
                    "min_purchase_amount",
                )
            },
        ),
        (
            "محدودیت‌ها",
            {"fields": ("max_usage", "current_usage", "valid_from", "valid_to")},
        ),
        (
            "اطلاعات اضافی",
            {"fields": ("created_date", "updated_date"), "classes": ("collapse",)},
        ),
    )

    def discount_display(self, obj):
        """Display discount in readable format."""
        if obj.discount_amount > 0:
            return f"{obj.discount_amount:,} تومان"
        return f"%{obj.discount_percentage}"

    discount_display.short_description = "تخفیف"

    def usage_display(self, obj):
        """Display usage statistics."""
        percentage = (
            (obj.current_usage / obj.max_usage * 100) if obj.max_usage > 0 else 0
        )
        return f"{obj.current_usage} / {obj.max_usage} ({percentage:.0f}%)"

    usage_display.short_description = "استفاده"

    def validity_display(self, obj):
        """Display validity status."""
        if obj.is_valid():
            return format_html('<span style="color: green;">✓ فعال</span>')
        return format_html('<span style="color: red;">✗ منقضی شده</span>')

    validity_display.short_description = "اعتبار"
