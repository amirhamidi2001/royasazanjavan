from django import template
from django.utils.safestring import mark_safe
from django.db.models import Count, Q

# import markdown
from ..models import Article, Category, Tag
from django.contrib.auth import get_user_model

User = get_user_model()
register = template.Library()


# ==========================================
# Simple Tags - Basic values
# ==========================================


@register.simple_tag
def total_articles():
    """Return the total number of published articles."""
    return Article.published.count()


@register.simple_tag
def total_categories():
    """Return the number of active categories with published articles."""
    return (
        Category.objects.annotate(
            article_count=Count("articles", filter=Q(articles__status="published"))
        )
        .filter(article_count__gt=0)
        .count()
    )


@register.simple_tag
def total_tags():
    """Return the number of active tags with published articles."""
    return (
        Tag.objects.annotate(
            article_count=Count("articles", filter=Q(articles__status="published"))
        )
        .filter(article_count__gt=0)
        .count()
    )


@register.simple_tag
def get_categories_with_count():
    """Return categories annotated with their published article count."""
    return (
        Category.objects.annotate(
            article_count=Count("articles", filter=Q(articles__status="published"))
        )
        .filter(article_count__gt=0)
        .order_by("-article_count")
    )


@register.simple_tag
def get_tags_with_count(limit=20):
    """Return tags annotated with their published article count."""
    return (
        Tag.objects.annotate(
            article_count=Count("articles", filter=Q(articles__status="published"))
        )
        .filter(article_count__gt=0)
        .order_by("-article_count")[:limit]
    )


@register.simple_tag
def get_top_authors(limit=10):
    """Return top authors ordered by number of published articles."""
    return (
        User.objects.filter(articles__status="published")
        .annotate(article_count=Count("articles"))
        .order_by("-article_count")
        .distinct()[:limit]
    )


@register.simple_tag
def get_most_viewed_articles(limit=5):
    """Return the most viewed published articles."""
    return Article.published.order_by("-view_count")[:limit]


@register.simple_tag
def get_latest_articles(limit=5):
    """Return the latest published articles."""
    return Article.published.order_by("-published_at")[:limit]


@register.simple_tag
def get_trending_articles(limit=5):
    """Return trending articles based on creation date."""
    return Article.published.order_by("-created_at")[:limit]


@register.simple_tag
def get_random_articles(limit=3):
    """Return random published articles."""
    return Article.published.order_by("?")[:limit]


# ==========================================
# Inclusion Tags - Template components
# ==========================================


@register.inclusion_tag("articles/partials/latest_articles_widget.html")
def show_latest_articles(count=5):
    """Render widget displaying the latest articles."""
    latest_articles = Article.published.select_related("author")[:count]
    return {"articles": latest_articles}


@register.inclusion_tag("articles/partials/popular_articles_widget.html")
def show_popular_articles(count=5):
    """Render widget displaying the most popular articles."""
    popular_articles = Article.published.select_related("author").order_by(
        "-view_count"
    )[:count]
    return {"articles": popular_articles}


@register.inclusion_tag("articles/partials/categories_widget.html")
def show_categories_widget():
    """Render widget displaying active categories."""
    categories = (
        Category.objects.annotate(
            article_count=Count("articles", filter=Q(articles__status="published"))
        )
        .filter(article_count__gt=0)
        .order_by("-article_count")
    )
    return {"categories": categories}


@register.inclusion_tag("articles/partials/tags_cloud.html")
def show_tags_cloud(limit=30):
    """Render tag cloud widget."""
    tags = (
        Tag.objects.annotate(
            article_count=Count("articles", filter=Q(articles__status="published"))
        )
        .filter(article_count__gt=0)
        .order_by("-article_count")[:limit]
    )
    return {"tags": tags}


@register.inclusion_tag("articles/partials/article_card.html")
def show_article_card(article):
    """Render a single article card component."""
    return {"article": article}


@register.inclusion_tag("articles/partials/breadcrumb.html", takes_context=True)
def show_breadcrumb(context):
    """Render breadcrumb navigation."""
    return {"request": context["request"]}


# ==========================================
# Filters
# ==========================================

# @register.filter(name='markdown')
# def markdown_format(text):
#     """Convert Markdown text to safe HTML."""
#     return mark_safe(markdown.markdown(text, extensions=['extra', 'codehilite']))


@register.filter
def reading_time(text):
    """Calculate reading time assuming 200 words per minute."""
    if text:
        words = len(text.split())
        minutes = words // 200
        return max(1, minutes)
    return 1


@register.filter
def truncate_words_html(text, num_words):
    """Truncate HTML text to a specific number of words while stripping tags."""
    from django.utils.html import strip_tags

    plain_text = strip_tags(text)
    words = plain_text.split()[:num_words]
    return " ".join(words) + ("..." if len(plain_text.split()) > num_words else "")


@register.filter
def format_number(value):
    """Format large numbers into a readable form (e.g. 1000 -> 1K)."""
    try:
        value = int(value)
        if value >= 1000000:
            return f"{value/1000000:.1f}M"
        elif value >= 1000:
            return f"{value/1000:.1f}K"
        return str(value)
    except (ValueError, TypeError):
        return value


# @register.filter
# def persian_date(value):
#     """Convert Gregorian date to Jalali date (requires jdatetime)."""
#     try:
#         import jdatetime
#         if value:
#             jalali = jdatetime.datetime.fromgregorian(datetime=value)
#             return jalali.strftime('%Y/%m/%d')
#     except ImportError:
#         pass
#     return value.strftime('%Y/%m/%d') if value else ''


# ==========================================
# Assignment Tags - Variable assignment
# ==========================================


@register.simple_tag
def get_article_by_slug(slug):
    """Return a published article by its slug."""
    try:
        return Article.published.get(slug=slug)
    except Article.DoesNotExist:
        return None


@register.simple_tag
def get_category_by_slug(slug):
    """Return a category by its slug."""
    try:
        return Category.objects.get(slug=slug)
    except Category.DoesNotExist:
        return None


@register.simple_tag
def get_articles_by_category(category_slug, limit=5):
    """Return published articles belonging to a specific category."""
    try:
        category = Category.objects.get(slug=category_slug)
        return Article.published.filter(categories=category)[:limit]
    except Category.DoesNotExist:
        return Article.published.none()


# ==========================================
# URL Helper Tags
# ==========================================


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """Replace or append query parameters for pagination."""
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()


@register.simple_tag(takes_context=True)
def get_filter_url(context, filter_type, value):
    """Build a URL with a specific filter applied."""
    query = context["request"].GET.copy()
    query[filter_type] = value
    if "page" in query:
        del query["page"]
    return query.urlencode()


@register.simple_tag(takes_context=True)
def remove_filter(context, filter_type):
    """Remove a specific filter from the current URL."""
    query = context["request"].GET.copy()
    if filter_type in query:
        del query[filter_type]
    if "page" in query:
        del query["page"]
    return query.urlencode()


@register.simple_tag(takes_context=True)
def is_active_filter(context, filter_type, value):
    """Check whether a filter is currently active."""
    return context["request"].GET.get(filter_type) == value


# ==========================================
# Conditional Tags
# ==========================================


@register.simple_tag
def article_has_category(article, category_slug):
    """Check whether an article belongs to a specific category."""
    return article.categories.filter(slug=category_slug).exists()


@register.simple_tag
def article_has_tag(article, tag_slug):
    """Check whether an article has a specific tag."""
    return article.tags.filter(slug=tag_slug).exists()


@register.inclusion_tag("articles/latest_articles.html")
def show_latest_articles(count=8):
    # Using the 'published' manager you defined in your model
    articles = Article.published.all()[:count]
    return {"articles": articles}
