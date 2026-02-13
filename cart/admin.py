from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import CartModel, CartItemModel


class CartItemInline(admin.TabularInline):
    """Inline admin for cart items"""

    model = CartItemModel
    extra = 0
    readonly_fields = (
        "created_date",
        "get_product_name",
        "get_product_type",
        "get_price",
    )
    fields = (
        "get_product_type",
        "get_product_name",
        "quantity",
        "get_price",
        "created_date",
    )
    can_delete = True

    def get_product_name(self, obj):
        """نمایش نام محصول"""
        if obj.content_object:
            return getattr(obj.content_object, "title", "Unknown")
        return "-"

    get_product_name.short_description = "نام محصول"

    def get_product_type(self, obj):
        """نمایش نوع محصول"""
        return obj.content_type.model if obj.content_type else "-"

    get_product_type.short_description = "نوع"

    def get_price(self, obj):
        """نمایش قیمت"""
        return f"{obj.get_total_price():,} تومان"

    get_price.short_description = "قیمت کل"


@admin.register(CartModel)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "get_items_count",
        "get_total_price",
        "updated_date",
        "created_date",
    )
    list_filter = ("created_date", "updated_date")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    readonly_fields = (
        "created_date",
        "updated_date",
        "get_items_count",
        "get_total_price",
    )
    inlines = [CartItemInline]

    fieldsets = (
        ("اطلاعات کاربر", {"fields": ("user",)}),
        ("اطلاعات سبد", {"fields": ("get_items_count", "get_total_price")}),
        (
            "تاریخ‌ها",
            {"fields": ("created_date", "updated_date"), "classes": ("collapse",)},
        ),
    )

    def get_items_count(self, obj):
        """تعداد آیتم‌های سبد"""
        return obj.get_items_count()

    get_items_count.short_description = "تعداد آیتم‌ها"

    def get_total_price(self, obj):
        """مجموع قیمت سبد"""
        return f"{obj.get_total_price():,} تومان"

    get_total_price.short_description = "مجموع قیمت"


@admin.register(CartItemModel)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_user",
        "get_product_type",
        "get_product_name",
        "quantity",
        "get_total_price_display",
        "created_date",
    )
    list_filter = ("content_type", "created_date")
    search_fields = (
        "cart__user__email",
        "cart__user__first_name",
        "cart__user__last_name",
    )
    readonly_fields = ("created_date", "get_product_info", "get_total_price_display")

    fieldsets = (
        ("سبد خرید", {"fields": ("cart",)}),
        ("محصول", {"fields": ("content_type", "object_id", "get_product_info")}),
        ("جزئیات", {"fields": ("quantity", "get_total_price_display", "created_date")}),
    )

    def get_user(self, obj):
        """نمایش کاربر"""
        return obj.cart.user.email

    get_user.short_description = "کاربر"
    get_user.admin_order_field = "cart__user__email"

    def get_product_type(self, obj):
        """نمایش نوع محصول"""
        if obj.content_type:
            return obj.content_type.model
        return "-"

    get_product_type.short_description = "نوع محصول"
    get_product_type.admin_order_field = "content_type__model"

    def get_product_name(self, obj):
        """نمایش نام محصول"""
        if obj.content_object:
            return getattr(obj.content_object, "title", "Unknown")
        return "محصول حذف شده"

    get_product_name.short_description = "نام محصول"

    def get_product_info(self, obj):
        """نمایش اطلاعات کامل محصول"""
        if not obj.content_object:
            return "محصول موجود نیست"

        product = obj.content_object
        info = f"نام: {getattr(product, 'title', 'Unknown')}<br>"
        info += f"نوع: {obj.content_type.model}<br>"

        if obj.content_type.model == "course":
            info += f"مدرس: {getattr(product.instructor, 'email', 'Unknown')}<br>"
            info += f"قیمت: {product.price:,} تومان"
        elif obj.content_type.model == "product":
            info += f"قیمت نهایی: {product.get_final_price():,} تومان<br>"
            if product.is_discounted():
                info += f"<span style='color: red;'>تخفیف: {product.get_discount_percentage()}%</span>"

        return info

    get_product_info.short_description = "اطلاعات محصول"
    get_product_info.allow_tags = True

    def get_total_price_display(self, obj):
        """نمایش قیمت کل"""
        return f"{obj.get_total_price():,} تومان"

    get_total_price_display.short_description = "قیمت کل"

    def has_add_permission(self, request):
        """جلوگیری از افزودن دستی آیتم از ادمین"""
        return False
