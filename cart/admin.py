from django.contrib import admin
from .models import CartModel, CartItemModel


class CartItemInline(admin.TabularInline):
    """Inline admin for cart items."""

    model = CartItemModel
    extra = 0
    readonly_fields = ("created_date",)
    fields = ("product", "quantity", "created_date")
    raw_id_fields = ("product",)


@admin.register(CartModel)
class CartAdmin(admin.ModelAdmin):
    """Admin interface for Cart model."""

    list_display = (
        "user",
        "get_items_count",
        "get_total_price",
        "updated_date",
        "created_date",
    )
    list_filter = ("created_date", "updated_date")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    readonly_fields = ("created_date", "updated_date")
    inlines = [CartItemInline]

    def get_items_count(self, obj):
        return obj.get_items_count()

    get_items_count.short_description = "تعداد آیتم‌ها"

    def get_total_price(self, obj):
        return f"{obj.get_total_price():,} تومان"

    get_total_price.short_description = "مجموع قیمت"


@admin.register(CartItemModel)
class CartItemAdmin(admin.ModelAdmin):
    """Admin interface for CartItem model."""

    list_display = ("cart", "product", "quantity", "get_total_price", "created_date")
    list_filter = ("created_date",)
    search_fields = ("cart__user__email", "product__title")
    readonly_fields = ("created_date", "get_total_price")
    raw_id_fields = ("cart", "product")

    def get_total_price(self, obj):
        return f"{obj.get_total_price():,} تومان"

    get_total_price.short_description = "قیمت کل"
