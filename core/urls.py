"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from website.views import Custom404View, ads_txt
from django.contrib.sitemaps.views import sitemap
from articles.sitemaps import ArticleSitemap
from courses.sitemaps import CourseSitemap
from shop.sitemaps import ProductSitemap
from website.sitemaps import StaticViewSitemap
from decouple import config

sitemaps = {
    "static": StaticViewSitemap,
    "articles": ArticleSitemap,
    "courses": CourseSitemap,
    "products": ProductSitemap,
}

ADMIN_URL = config("ADMIN_URL")

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    path("", include("website.urls")),
    path("accounts/", include("accounts.urls")),
    path("accounts/oauth/", include("social_django.urls", namespace="social")),
    path("articles/", include("articles.urls")),
    path("cart/", include("cart.urls")),
    path("courses/", include("courses.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("files/", include("files.urls")),
    path("orders/", include("orders.urls")),
    path("shop/", include("shop.urls")),
    path("robots.txt", include("robots.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("ads.txt", ads_txt),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = Custom404View.as_view()
