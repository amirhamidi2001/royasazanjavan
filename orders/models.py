from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from courses.models import Course
import uuid


class OrderStatusChoices(models.TextChoices):
    """Order status choices."""

    PENDING = "pending", _("در انتظار پرداخت")
    PROCESSING = "processing", _("در حال پردازش")
    PAID = "paid", _("پرداخت شده")
    FAILED = "failed", _("پرداخت ناموفق")
    CANCELLED = "cancelled", _("لغو شده")
    REFUNDED = "refunded", _("بازگشت داده شده")


class Order(models.Model):
    """Model representing a course order."""

    # Order Identification
    order_number = models.CharField(
        _("شماره سفارش"), max_length=50, unique=True, editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name=_("کاربر"),
    )

    # Customer Information
    first_name = models.CharField(_("نام"), max_length=100)
    last_name = models.CharField(_("نام خانوادگی"), max_length=100)
    email = models.EmailField(_("ایمیل"))
    phone = models.CharField(_("تلفن"), max_length=20)

    # Address Information
    address = models.TextField(_("آدرس"), blank=True)
    apartment = models.CharField(_("واحد/پلاک"), max_length=100, blank=True)
    city = models.CharField(_("شهر"), max_length=100, blank=True)
    state = models.CharField(_("استان"), max_length=100, blank=True)
    zip_code = models.CharField(_("کد پستی"), max_length=20, blank=True)
    country = models.CharField(_("کشور"), max_length=100, default="IR")

    # Payment Information
    total_price = models.DecimalField(
        _("مبلغ کل"), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    discount_amount = models.DecimalField(
        _("مبلغ تخفیف"),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    tax_amount = models.DecimalField(
        _("مبلغ مالیات"),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    final_price = models.DecimalField(
        _("مبلغ نهایی"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    # Payment Gateway Information (ZarinPal)
    is_paid = models.BooleanField(_("پرداخت شده"), default=False)
    zarinpal_authority = models.CharField(
        _("کد پیگیری زرین‌پال"), max_length=255, blank=True, null=True
    )
    zarinpal_ref_id = models.CharField(
        _("شماره مرجع زرین‌پال"), max_length=255, blank=True, null=True
    )
    payment_date = models.DateTimeField(_("تاریخ پرداخت"), blank=True, null=True)

    # Order Status
    status = models.CharField(
        _("وضعیت"),
        max_length=20,
        choices=OrderStatusChoices.choices,
        default=OrderStatusChoices.PENDING,
    )

    # Additional Information
    notes = models.TextField(_("یادداشت"), blank=True)

    # Timestamps
    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاریخ ایجاد")
    )
    updated_date = models.DateTimeField(
        auto_now=True, verbose_name=_("تاریخ بروزرسانی")
    )

    class Meta:
        verbose_name = _("سفارش")
        verbose_name_plural = _("سفارش‌ها")
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["-created_date"]),
            models.Index(fields=["user", "-created_date"]),
            models.Index(fields=["order_number"]),
            models.Index(fields=["zarinpal_authority"]),
        ]

    def __str__(self):
        return f"Order {self.order_number} - {self.user.email}"

    def save(self, *args, **kwargs):
        """Generate order number if not exists."""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_order_number():
        """Generate unique order number."""
        import random
        import string
        from django.utils import timezone

        # Format: ORD-YYYYMMDD-RANDOM6
        date_part = timezone.now().strftime("%Y%m%d")
        random_part = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
        return f"ORD-{date_part}-{random_part}"

    def get_total_items(self):
        """Get total number of items in order."""
        return self.items.count()

    def get_full_name(self):
        """Get customer full name."""
        return f"{self.first_name} {self.last_name}"

    def mark_as_paid(self, ref_id):
        """Mark order as paid and update payment information."""
        from django.utils import timezone

        self.is_paid = True
        self.status = OrderStatusChoices.PAID
        self.zarinpal_ref_id = ref_id
        self.payment_date = timezone.now()
        self.save()

        # Enroll user in courses
        self.enroll_user_in_courses()

    def enroll_user_in_courses(self):
        """Enroll user in all courses after successful payment."""
        from courses.models import CourseProgress

        for item in self.items.all():
            # Add user to course students
            if self.user not in item.course.students.all():
                # Create CourseProgress which adds user to students
                CourseProgress.objects.get_or_create(user=self.user, course=item.course)

    def can_be_paid(self):
        """Check if order can be paid."""
        return self.status == OrderStatusChoices.PENDING and not self.is_paid


class OrderItem(models.Model):
    """Model representing items in an order."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name=_("سفارش")
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name=_("دوره"),
    )
    price = models.DecimalField(
        _("قیمت"), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveIntegerField(
        _("تعداد"), default=1, validators=[MinValueValidator(1)]
    )

    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاریخ افزودن")
    )

    class Meta:
        verbose_name = _("آیتم سفارش")
        verbose_name_plural = _("آیتم‌های سفارش")
        unique_together = ("order", "course")

    def __str__(self):
        return f"{self.course.title} - Order {self.order.order_number}"

    def get_total_price(self):
        """Calculate total price for this item."""
        return self.quantity * self.price


class Coupon(models.Model):
    """Model for discount coupons."""

    code = models.CharField(_("کد تخفیف"), max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField(
        _("درصد تخفیف"),
        validators=[MinValueValidator(1), MinValueValidator(100)],
        help_text=_("درصد تخفیف (1-100)"),
    )
    discount_amount = models.DecimalField(
        _("مبلغ تخفیف"),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("اگر مبلغ ثابت تخفیف دارید"),
    )
    max_usage = models.PositiveIntegerField(
        _("حداکثر استفاده"), default=1, help_text=_("تعداد دفعات قابل استفاده")
    )
    current_usage = models.PositiveIntegerField(_("تعداد استفاده شده"), default=0)
    min_purchase_amount = models.DecimalField(
        _("حداقل مبلغ خرید"),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField(_("فعال"), default=True)
    valid_from = models.DateTimeField(_("تاریخ شروع"))
    valid_to = models.DateTimeField(_("تاریخ پایان"))

    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاریخ ایجاد")
    )
    updated_date = models.DateTimeField(
        auto_now=True, verbose_name=_("تاریخ بروزرسانی")
    )

    class Meta:
        verbose_name = _("کد تخفیف")
        verbose_name_plural = _("کدهای تخفیف")
        ordering = ["-created_date"]

    def __str__(self):
        return self.code

    def is_valid(self):
        """Check if coupon is valid."""
        from django.utils import timezone

        now = timezone.now()

        return (
            self.is_active
            and self.valid_from <= now <= self.valid_to
            and self.current_usage < self.max_usage
        )

    def can_use(self, total_amount):
        """Check if coupon can be used for given amount."""
        return self.is_valid() and total_amount >= self.min_purchase_amount

    def calculate_discount(self, total_amount):
        """Calculate discount amount."""
        if self.discount_amount > 0:
            return min(self.discount_amount, total_amount)
        elif self.discount_percentage > 0:
            return (total_amount * self.discount_percentage) / 100
        return 0

    def use_coupon(self):
        """Increment usage counter."""
        self.current_usage += 1
        self.save()
