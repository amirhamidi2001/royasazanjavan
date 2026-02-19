from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from articles.models import Article, Category, Tag, Comment
from dashboard.mixins import (
    DashboardMixin,
    SuccessMessageMixin,
    DeleteSuccessMessageMixin,
)


class ArticleListView(DashboardMixin, ListView):
    """
    Display a paginated list of articles in the dashboard.
    """

    model = Article
    template_name = "dashboard/articles/article_list.html"
    context_object_name = "articles"
    paginate_by = 20
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Return optimized queryset with filtering and searching support.
        """
        queryset = (
            super()
            .get_queryset()
            .select_related("author")
            .prefetch_related("categories", "tags")
        )
        search_query = self.request.GET.get("search", "")
        status_filter = self.request.GET.get("status", "")

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(excerpt__icontains=search_query)
                | Q(author__email__icontains=search_query)
            )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add filter values and UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["title"] = "مدیریت مقالات"
        context["create_url"] = reverse_lazy("dashboard:articles:article-create")

        return context


class ArticleCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """
    Create a new article from the dashboard.
    """

    model = Article
    template_name = "dashboard/articles/article_form.html"
    fields = [
        "title",
        "slug",
        "excerpt",
        "content",
        "featured_image",
        "categories",
        "tags",
        "status",
    ]
    success_url = reverse_lazy("dashboard:articles:article-list")
    success_message = "مقاله با موفقیت ایجاد شد."

    def get_context_data(self, **kwargs):
        """
        Add UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد مقاله جدید"
        context["submit_text"] = "انتشار مقاله"
        return context

    def form_valid(self, form):
        """
        Automatically assign the current user as author.
        """
        form.instance.author = self.request.user
        return super().form_valid(form)


class ArticleUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    Update an existing article.
    """

    model = Article
    template_name = "dashboard/articles/article_form.html"
    fields = [
        "title",
        "slug",
        "excerpt",
        "content",
        "featured_image",
        "categories",
        "tags",
        "status",
    ]
    success_url = reverse_lazy("dashboard:articles:article-list")
    success_message = "مقاله با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        """
        Add UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش مقاله"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class ArticleDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    Delete an article from the dashboard.
    """

    model = Article
    template_name = "dashboard/articles/article_confirm_delete.html"
    success_url = reverse_lazy("dashboard:articles:article-list")
    delete_success_message = "مقاله با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        """
        Add UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف مقاله"
        return context


class CategoryListView(DashboardMixin, ListView):
    """
    Display a paginated list of categories.
    """

    model = Category
    template_name = "dashboard/articles/category_list.html"
    context_object_name = "categories"
    paginate_by = 20
    ordering = ["name"]

    def get_queryset(self):
        """
        Return filtered queryset based on search query.
        """
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add search and UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["title"] = "مدیریت دسته‌بندی‌ها"
        context["create_url"] = reverse_lazy("dashboard:articles:category-create")
        return context


class CategoryCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """
    Create a new category.
    """

    model = Category
    template_name = "dashboard/articles/category_form.html"
    fields = ["name", "slug", "description"]
    success_url = reverse_lazy("dashboard:articles:category-list")
    success_message = "دسته‌بندی با موفقیت ایجاد شد."

    def get_context_data(self, **kwargs):
        """
        Add UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد دسته‌بندی جدید"
        context["submit_text"] = "ایجاد دسته‌بندی"
        return context


class CategoryUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    Update an existing category.
    """

    model = Category
    template_name = "dashboard/articles/category_form.html"
    fields = ["name", "slug", "description"]
    success_url = reverse_lazy("dashboard:articles:category-list")
    success_message = "دسته‌بندی با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        """
        Add UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش دسته‌بندی"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class CategoryDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    Delete a category.
    """

    model = Category
    template_name = "dashboard/articles/category_confirm_delete.html"
    success_url = reverse_lazy("dashboard:articles:category-list")
    delete_success_message = "دسته‌بندی با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        """
        Add UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف دسته‌بندی"
        return context


class TagListView(DashboardMixin, ListView):
    """
    Display a paginated list of tags.
    """

    model = Tag
    template_name = "dashboard/articles/tag_list.html"
    context_object_name = "tags"
    paginate_by = 20
    ordering = ["name"]

    def get_queryset(self):
        """
        Return filtered queryset based on search query.
        """
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add search and UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["title"] = "مدیریت برچسب‌ها"
        context["create_url"] = reverse_lazy("dashboard:articles:tag-create")
        return context


class TagCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    """
    Create a new tag.
    """

    model = Tag
    template_name = "dashboard/articles/tag_form.html"
    fields = ["name", "slug"]
    success_url = reverse_lazy("dashboard:articles:tag-list")
    success_message = "برچسب با موفقیت ایجاد شد."

    def get_context_data(self, **kwargs):
        """
        Add UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "ایجاد برچسب جدید"
        context["submit_text"] = "ایجاد برچسب"
        return context


class TagUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    Update an existing tag.
    """

    model = Tag
    template_name = "dashboard/articles/tag_form.html"
    fields = ["name", "slug"]
    success_url = reverse_lazy("dashboard:articles:tag-list")
    success_message = "برچسب با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        """
        Add UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش برچسب"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class TagDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    Delete a tag.
    """

    model = Tag
    template_name = "dashboard/articles/tag_confirm_delete.html"
    success_url = reverse_lazy("dashboard:articles:tag-list")
    delete_success_message = "برچسب با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        """
        Add UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف برچسب"
        return context


class CommentListView(DashboardMixin, ListView):
    """
    Display a paginated list of comments.

    Supports search and filtering by approval status.
    """

    model = Comment
    template_name = "dashboard/articles/comment_list.html"
    context_object_name = "comments"
    paginate_by = 20
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Return optimized queryset with search and approval filters.
        """
        queryset = super().get_queryset().select_related("article")
        search_query = self.request.GET.get("search", "")
        approved_filter = self.request.GET.get("approved", "")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(body__icontains=search_query)
            )

        if approved_filter == "yes":
            queryset = queryset.filter(is_approved=True)
        elif approved_filter == "no":
            queryset = queryset.filter(is_approved=False)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add filter values and UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["approved_filter"] = self.request.GET.get("approved", "")
        context["title"] = "مدیریت نظرات"
        return context


class CommentUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    """
    Update an existing comment.
    """

    model = Comment
    template_name = "dashboard/articles/comment_form.html"
    fields = ["name", "email", "website", "body", "is_approved"]
    success_url = reverse_lazy("dashboard:articles:comment-list")
    success_message = "نظر با موفقیت ویرایش شد."

    def get_context_data(self, **kwargs):
        """
        Add UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "ویرایش نظر"
        context["submit_text"] = "ذخیره تغییرات"
        return context


class CommentDeleteView(DashboardMixin, DeleteSuccessMessageMixin, DeleteView):
    """
    Delete a comment.
    """

    model = Comment
    template_name = "dashboard/articles/comment_confirm_delete.html"
    success_url = reverse_lazy("dashboard:articles:comment-list")
    delete_success_message = "نظر با موفقیت حذف شد."

    def get_context_data(self, **kwargs):
        """
        Add UI metadata to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "حذف نظر"
        return context
