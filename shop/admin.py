from django.contrib import admin
from .models import Category, Product, ProductFeature


class ProductFeatureInline(admin.TabularInline):
    """
    Inline admin for Product Features
    """

    model = ProductFeature
    extra = 3
    fields = ("feature_name", "feature_value", "order")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Category model
    """

    list_display = ("name", "slug", "parent", "is_active", "created_at")
    list_filter = ("is_active", "parent", "created_at")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)
    ordering = ("name",)

    fieldsets = (
        ("Basic Information", {"fields": ("name", "slug", "parent", "description")}),
        ("Status", {"fields": ("is_active",)}),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for Product model
    """

    list_display = (
        "title",
        "product_type",
        "category",
        "price",
        "discounted_price",
        "stock",
        "is_free",
        "is_active",
        "is_featured",
        "created_at",
    )
    list_filter = (
        "is_active",
        "is_featured",
        "is_free",
        "product_type",
        "category",
        "created_at",
    )
    search_fields = ("title", "slug", "description", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_active", "is_featured", "is_free", "stock")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProductFeatureInline]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "slug", "category", "product_type")},
        ),
        ("Description", {"fields": ("short_description", "description")}),
        (
            "Pricing",
            {
                "fields": ("price", "discounted_price", "is_free"),
                "description": 'If "Is Free" is checked, prices will be set to 0 automatically.',
            },
        ),
        ("Inventory", {"fields": ("stock",)}),
        ("Media", {"fields": ("image",)}),
        ("Status", {"fields": ("is_active", "is_featured")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def save_model(self, request, obj, form, change):
        """
        Custom save to handle free products
        """
        super().save_model(request, obj, form, change)


@admin.register(ProductFeature)
class ProductFeatureAdmin(admin.ModelAdmin):
    """
    Admin configuration for Product Feature model
    """

    list_display = ("product", "feature_name", "feature_value", "order")
    list_filter = ("product",)
    search_fields = ("product__title", "feature_name", "feature_value")
    ordering = ("product", "order")
