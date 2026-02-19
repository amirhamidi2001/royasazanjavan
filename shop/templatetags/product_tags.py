from django import template
from django.utils import timezone
from datetime import timedelta
from ..models import Product

register = template.Library()


@register.inclusion_tag("shop/product_card.html")
def render_product_card(product):
    # Logic for "New" badge (e.g., created in the last 7 days)
    is_new = product.created_at >= timezone.now() - timedelta(days=7)

    return {
        "product": product,
        "is_new": is_new,
    }


@register.simple_tag
def get_free_products(limit=3):
    return Product.objects.filter(is_free=True, is_active=True)[:limit]


@register.simple_tag
def get_latest_products(limit=3):
    return Product.objects.filter(is_active=True).order_by("-created_at")[:limit]


@register.simple_tag
def get_discounted_products(limit=3):
    return Product.objects.filter(
        discounted_price__isnull=False, is_active=True
    ).exclude(discounted_price=0)[:limit]
