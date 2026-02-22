from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages like Home, Contact, etc."""

    priority = 0.5
    changefreq = "monthly"

    def items(self):
        # Return the names of the views/URLs you want to index
        # Adjust these names based on your website/urls.py
        return ["website:index", "website:contact", "website:about"]

    def location(self, item):
        return reverse(item)
