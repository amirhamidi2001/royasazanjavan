# shop/management/commands/create_sample_products.py
"""
Management command to create sample products for testing

Usage:
    python manage.py create_sample_products
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Category, Product, ProductFeature
from decimal import Decimal
import random


class Command(BaseCommand):
    help = "Create sample products for testing the shop app"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating sample categories...")

        # Create main categories
        educational_cat = Category.objects.get_or_create(
            name="بسته‌های آموزشی",
            defaults={"slug": slugify("بسته‌های آموزشی", allow_unicode=True)},
        )[0]

        software_cat = Category.objects.get_or_create(
            name="نرم‌افزارها",
            defaults={"slug": slugify("نرم‌افزارها", allow_unicode=True)},
        )[0]

        book_cat = Category.objects.get_or_create(
            name="کتاب‌ها", defaults={"slug": slugify("کتاب‌ها", allow_unicode=True)}
        )[0]

        # Create subcategories
        programming_cat = Category.objects.get_or_create(
            name="برنامه‌نویسی",
            defaults={
                "slug": slugify("برنامه‌نویسی", allow_unicode=True),
                "parent": educational_cat,
            },
        )[0]

        design_cat = Category.objects.get_or_create(
            name="طراحی",
            defaults={
                "slug": slugify("طراحی", allow_unicode=True),
                "parent": educational_cat,
            },
        )[0]

        self.stdout.write(self.style.SUCCESS("Categories created!"))

        # Sample products data
        products_data = [
            {
                "title": "دوره جامع Django",
                "category": programming_cat,
                "product_type": "educational_package",
                "short_description": "آموزش کامل فریمورک Django از صفر تا صد",
                "description": "در این دوره جامع، تمامی مفاهیم Django از پایه تا پیشرفته آموزش داده می‌شود. شامل پروژه‌های عملی و واقعی.",
                "price": Decimal("250000"),
                "discounted_price": Decimal("199000"),
                "stock": 100,
                "features": [
                    ("مدت زمان", "40 ساعت"),
                    ("سطح", "مقدماتی تا پیشرفته"),
                    ("پروژه‌ها", "5 پروژه عملی"),
                ],
            },
            {
                "title": "دوره Python مقدماتی",
                "category": programming_cat,
                "product_type": "educational_package",
                "short_description": "شروع برنامه‌نویسی با Python",
                "description": "یادگیری اصول برنامه‌نویسی با زبان Python. مناسب برای مبتدیان.",
                "price": Decimal("150000"),
                "stock": 150,
                "is_free": True,
                "features": [
                    ("مدت زمان", "20 ساعت"),
                    ("سطح", "مقدماتی"),
                    ("نیازمندی‌ها", "بدون پیش‌نیاز"),
                ],
            },
            {
                "title": "بسته طراحی UI/UX",
                "category": design_cat,
                "product_type": "educational_package",
                "short_description": "طراحی رابط کاربری و تجربه کاربری حرفه‌ای",
                "description": "آموزش اصول طراحی UI/UX با استفاده از Figma و Adobe XD",
                "price": Decimal("300000"),
                "discounted_price": Decimal("240000"),
                "stock": 80,
                "features": [
                    ("مدت زمان", "35 ساعت"),
                    ("ابزارها", "Figma, Adobe XD"),
                    ("پروژه نهایی", "طراحی اپلیکیشن کامل"),
                ],
            },
            {
                "title": "نرم‌افزار مدیریت پروژه",
                "category": software_cat,
                "product_type": "software_package",
                "short_description": "نرم‌افزار حرفه‌ای مدیریت پروژه",
                "description": "نرم‌افزار کامل برای مدیریت پروژه‌ها با قابلیت‌های پیشرفته",
                "price": Decimal("500000"),
                "stock": 50,
                "features": [
                    ("لایسنس", "یک کاربره"),
                    ("پشتیبانی", "1 سال"),
                    ("آپدیت", "رایگان"),
                ],
            },
            {
                "title": "کتاب الگوریتم‌ها و ساختمان داده",
                "category": book_cat,
                "product_type": "book",
                "short_description": "مرجع کامل الگوریتم‌ها به زبان فارسی",
                "description": "کتاب جامع الگوریتم‌ها و ساختمان داده با مثال‌های عملی",
                "price": Decimal("120000"),
                "discounted_price": Decimal("95000"),
                "stock": 200,
                "features": [
                    ("صفحات", "450 صفحه"),
                    ("فرمت", "PDF"),
                    ("زبان", "فارسی"),
                ],
            },
            {
                "title": "کتاب طراحی الگوها در Python",
                "category": book_cat,
                "product_type": "book",
                "short_description": "الگوهای طراحی در Python",
                "description": "آشنایی با Design Patterns در Python با مثال‌های کاربردی",
                "price": Decimal("85000"),
                "stock": 150,
                "features": [
                    ("صفحات", "320 صفحه"),
                    ("فرمت", "PDF"),
                    ("کد منبع", "شامل"),
                ],
            },
        ]

        self.stdout.write("Creating sample products...")

        for product_data in products_data:
            features = product_data.pop("features", [])

            # Create product
            product, created = Product.objects.get_or_create(
                title=product_data["title"],
                defaults={
                    **product_data,
                    "slug": slugify(product_data["title"], allow_unicode=True),
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {product.title}"))

                # Add features
                for idx, (name, value) in enumerate(features):
                    ProductFeature.objects.create(
                        product=product,
                        feature_name=name,
                        feature_value=value,
                        order=idx,
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Already exists: {product.title}")
                )

        self.stdout.write(self.style.SUCCESS("Sample products created successfully!"))
        self.stdout.write(f"Total products: {Product.objects.count()}")
        self.stdout.write(f"Total categories: {Category.objects.count()}")
