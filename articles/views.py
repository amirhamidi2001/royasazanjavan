from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count

from .models import Article, Comment, Category, Tag
from .forms import CommentForm
from django.contrib.auth import get_user_model

User = get_user_model()


class ArticleDetailView(DetailView):
    """
    Displays the detail page of a single published article.
    Handles view counting, approved comments, and comment submission.
    """

    model = Article
    template_name = "articles/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """
        Return only published articles with related data
        optimized using select_related and prefetch_related.
        """
        return Article.published.select_related("author").prefetch_related(
            "categories", "tags", "comments"
        )

    def get_object(self, queryset=None):
        """
        Retrieve the article object and increment view count
        once per session to avoid duplicate views.
        """
        article = super().get_object(queryset)

        session_key = f"viewed_article_{article.id}"
        if not self.request.session.get(session_key, False):
            article.increment_view_count()
            self.request.session[session_key] = True

        return article

    def get_context_data(self, **kwargs):
        """
        Add comments, comment form, reading time,
        and related articles to the template context.
        """
        context = super().get_context_data(**kwargs)
        article = self.get_object()

        # Approved top-level comments
        context["comments"] = article.get_approved_comments().filter(
            parent__isnull=True
        )

        # Comment form
        context.setdefault("comment_form", CommentForm())

        context["comment_count"] = article.get_comment_count()
        context["reading_time"] = article.get_reading_time()

        # Related articles based on shared categories
        context["related_articles"] = (
            Article.published.filter(categories__in=article.categories.all())
            .exclude(id=article.id)
            .distinct()[:3]
        )

        return context

    def post(self, request, *args, **kwargs):
        """
        Handle comment submission for the article,
        including optional reply (nested comments).
        """
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = self.object

            # Handle reply to another comment if provided
            parent_id = request.POST.get("parent_id")
            if parent_id:
                try:
                    comment.parent = Comment.objects.get(id=parent_id)
                except Comment.DoesNotExist:
                    pass

            comment.save()

            messages.success(
                request,
                "کامنت شما با موفقیت ثبت شد و پس از تأیید نمایش داده خواهد شد.",
            )
            return redirect(self.object.get_absolute_url() + "#blog-comments")

        messages.error(request, "خطا در ارسال کامنت. لطفاً فیلدها را بررسی کنید.")
        context = self.get_context_data()
        context["comment_form"] = form
        return self.render_to_response(context)


class ArticleListView(ListView):
    """
    Displays a paginated list of published articles
    with support for filtering, searching, and sorting.
    """

    model = Article
    template_name = "articles/article_list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        """
        Build the article queryset based on query parameters
        such as search, category, tag, author, and sorting.
        """
        queryset = Article.published.select_related("author").prefetch_related(
            "categories", "tags"
        )

        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(excerpt__icontains=search_query)
                | Q(content__icontains=search_query)
            )

        if category_slug := self.request.GET.get("category"):
            queryset = queryset.filter(categories__slug=category_slug)

        if tag_slug := self.request.GET.get("tag"):
            queryset = queryset.filter(tags__slug=tag_slug)

        if author_id := self.request.GET.get("author"):
            queryset = queryset.filter(author__id=author_id)

        sort_by = self.request.GET.get("sort", "-published_at")
        if sort_by in ["-published_at", "published_at", "-view_count", "title"]:
            queryset = queryset.order_by(sort_by)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        """
        Add featured content, filters, and auxiliary data
        such as categories, tags, and authors to context.
        """
        context = super().get_context_data(**kwargs)

        context["featured_article"] = Article.published.order_by("-view_count").first()
        context["secondary_articles"] = Article.published.order_by("-view_count")[1:3]

        context["top_stories"] = Article.published.order_by("-view_count")[:5]
        context["trending_articles"] = Article.published.order_by("-created_at")[:5]
        context["latest_articles"] = Article.published.order_by("-published_at")[:5]

        context["all_categories"] = Category.objects.annotate(
            article_count=Count("articles", filter=Q(articles__status="published"))
        ).filter(article_count__gt=0)

        context["all_tags"] = Tag.objects.annotate(
            article_count=Count("articles", filter=Q(articles__status="published"))
        ).filter(article_count__gt=0)[:20]

        context["active_authors"] = (
            User.objects.filter(articles__status="published")
            .annotate(article_count=Count("articles"))
            .distinct()[:10]
        )

        context["current_filters"] = {
            "search": self.request.GET.get("q", ""),
            "category": self.request.GET.get("category", ""),
            "tag": self.request.GET.get("tag", ""),
            "author": self.request.GET.get("author", ""),
            "sort": self.request.GET.get("sort", "-published_at"),
        }

        return context


class CategoryArticleListView(ListView):
    """
    Displays published articles belonging to a specific category.
    """

    model = Article
    template_name = "articles/category_list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return (
            Article.published.filter(categories=self.category)
            .select_related("author")
            .prefetch_related("categories", "tags")
        )

    def get_context_data(self, **kwargs):
        """
        Add category metadata and related categories to context.
        """
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["category_article_count"] = self.get_queryset().count()

        context["related_categories"] = (
            Category.objects.exclude(id=self.category.id)
            .annotate(
                article_count=Count("articles", filter=Q(articles__status="published"))
            )
            .filter(article_count__gt=0)[:5]
        )

        return context


class TagArticleListView(ListView):
    """
    Displays published articles associated with a specific tag.
    """

    model = Article
    template_name = "articles/tag_list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return (
            Article.published.filter(tags=self.tag)
            .select_related("author")
            .prefetch_related("categories", "tags")
        )

    def get_context_data(self, **kwargs):
        """
        Add tag metadata and related tags to context.
        """
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        context["tag_article_count"] = self.get_queryset().count()

        context["related_tags"] = (
            Tag.objects.exclude(id=self.tag.id)
            .annotate(
                article_count=Count("articles", filter=Q(articles__status="published"))
            )
            .filter(article_count__gt=0)[:10]
        )

        return context


class AuthorArticleListView(ListView):
    """
    Displays published articles written by a specific author.
    """

    model = Article
    template_name = "articles/author_list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        self.author = get_object_or_404(User, id=self.kwargs["author_id"])
        return (
            Article.published.filter(author=self.author)
            .select_related("author")
            .prefetch_related("categories", "tags")
        )

    def get_context_data(self, **kwargs):
        """
        Add author metadata and statistics to context.
        """
        context = super().get_context_data(**kwargs)
        context["article_author"] = self.author
        context["author_article_count"] = self.get_queryset().count()
        context["author_total_views"] = (
            self.get_queryset().aggregate(total_views=Count("view_count"))[
                "total_views"
            ]
            or 0
        )
        return context


class ArticleSearchView(ListView):
    """
    Provides advanced search across articles,
    categories, tags, and author names.
    """

    model = Article
    template_name = "articles/search_results.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        if not query:
            return Article.published.none()

        return (
            Article.published.filter(
                Q(title__icontains=query)
                | Q(excerpt__icontains=query)
                | Q(content__icontains=query)
                | Q(categories__name__icontains=query)
                | Q(tags__name__icontains=query)
                | Q(author__first_name__icontains=query)
                | Q(author__last_name__icontains=query)
            )
            .select_related("author")
            .prefetch_related("categories", "tags")
            .distinct()
        )

    def get_context_data(self, **kwargs):
        """
        Add search query and result count to context.
        """
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        context["search_count"] = self.get_queryset().count()
        return context
