from django.db import models
from django.conf import settings
from courses.models import Course


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
    """Model for items in a shopping cart."""

    cart = models.ForeignKey(
        CartModel,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سبد خرید",
    )
    product = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="cart_items", verbose_name="دوره"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ افزودن")

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product.title} - {self.cart.user.email}"

    def get_total_price(self):
        """Calculate total price for this item."""
        return self.quantity * self.product.price
