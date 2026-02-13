from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """
    Product Category Model with support for nested categories
    """

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("shop:product_list") + f"?category={self.slug}"

    def get_all_children(self):
        """Get all subcategories recursively"""
        children = list(self.subcategories.all())
        for child in list(children):
            children.extend(child.get_all_children())
        return children


class Product(models.Model):
    """
    Main Product Model for the Shop
    """

    PRODUCT_TYPE_CHOICES = [
        ("educational_package", "Educational Package"),
        ("software_package", "Software Package"),
        ("book", "Book"),
    ]

    # Basic Information
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True, allow_unicode=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    # Product Type
    product_type = models.CharField(
        max_length=50, choices=PRODUCT_TYPE_CHOICES, default="educational_package"
    )

    # Description
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)

    # Pricing
    price = models.DecimalField(
        max_digits=10, decimal_places=0, validators=[MinValueValidator(Decimal("0"))]
    )
    discounted_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
        help_text="Leave blank if no discount",
    )
    is_free = models.BooleanField(default=False, help_text="Mark product as free")

    # Inventory
    stock = models.PositiveIntegerField(default=0)

    # Media
    image = models.ImageField(upload_to="products/%Y/%m/", blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "-created_at"]),
            models.Index(fields=["product_type"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)

        # If marked as free, set prices to 0
        if self.is_free:
            self.price = Decimal("0")
            self.discounted_price = Decimal("0")

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("shop:product_detail", kwargs={"slug": self.slug})

    def get_final_price(self):
        """Return the final price (discounted or regular)"""
        if self.is_free:
            return Decimal("0")
        if self.discounted_price and self.discounted_price < self.price:
            return self.discounted_price
        return self.price

    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if (
            self.discounted_price
            and self.discounted_price < self.price
            and self.price > 0
        ):
            discount = ((self.price - self.discounted_price) / self.price) * 100
            return int(discount)
        return 0

    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0

    def is_discounted(self):
        """Check if product has a discount"""
        return self.discounted_price and self.discounted_price < self.price


class ProductFeature(models.Model):
    """
    Product Features/Specifications
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="features"
    )
    feature_name = models.CharField(max_length=200)
    feature_value = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0, help_text="Display order")

    class Meta:
        verbose_name = "Product Feature"
        verbose_name_plural = "Product Features"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.product.title} - {self.feature_name}: {self.feature_value}"
