from django.contrib.sitemaps import Sitemap
from .models import Article


class ArticleSitemap(Sitemap):
    """
    Sitemap for published articles.
    """

    changefreq = "weekly"
    priority = 0.9  # High priority for articles

    def items(self):
        # Using your custom 'published' manager to only index live articles
        return Article.published.all()

    def lastmod(self, obj):
        # Returns the last update time
        return obj.updated_at
