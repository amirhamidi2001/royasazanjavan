from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class CartModel(models.Model):
    """Model for user's shopping cart."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="کاربر",
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    def __str__(self):
        return f"Cart - {self.user.email}"

    def get_total_price(self):
        """Calculate total price of all items in cart."""
        return sum(item.get_total_price() for item in self.items.all())

    def get_items_count(self):
        """Get total number of items in cart."""
        return self.items.count()


class CartItemModel(models.Model):
    """
    Model for items in a shopping cart.
    Uses Generic Foreign Keys to support multiple product types (Course, Product, etc.)
    """

    cart = models.ForeignKey(
        CartModel,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سبد خرید",
    )

    # Generic Foreign Key fields
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="نوع محصول",
        limit_choices_to={"model__in": ("course", "product")},
    )
    object_id = models.PositiveIntegerField(verbose_name="شناسه محصول")
    content_object = GenericForeignKey("content_type", "object_id")

    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ افزودن")

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        unique_together = ("cart", "content_type", "object_id")
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        product_name = getattr(self.content_object, "title", "Unknown Product")
        return f"{product_name} - {self.cart.user.email}"

    def get_total_price(self):
        """Calculate total price for this item based on product type."""
        if not self.content_object:
            return 0

        # Get price based on product type
        if hasattr(self.content_object, "get_final_price"):
            # For Product model (from shop app)
            price = self.content_object.get_final_price()
        else:
            # For Course model (from courses app)
            price = getattr(self.content_object, "price", 0)

        return self.quantity * price

    def get_product_type(self):
        """Return the type of product (course or product)."""
        return self.content_type.model

    def is_active(self):
        """Check if the related product is still active."""
        if not self.content_object:
            return False
        return getattr(self.content_object, "is_active", True)
