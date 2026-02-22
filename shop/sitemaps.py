from django.contrib.sitemaps import Sitemap
from .models import Product


class ProductSitemap(Sitemap):
    """
    Sitemap for active products in the shop.
    """

    changefreq = "daily"  # Prices or stock might change frequently
    priority = 1.0  # Products are high value for SEO

    def items(self):
        # Only index products that are active
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at
