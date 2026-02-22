from django.contrib.sitemaps import Sitemap
from .models import Course


class CourseSitemap(Sitemap):
    """
    Sitemap for active courses.
    """

    changefreq = "weekly"
    priority = 0.8

    def items(self):
        # Only index courses that are marked as active
        return Course.objects.filter(is_active=True)

    def lastmod(self, obj):
        # Use the updated_date field from your model
        return obj.updated_date
