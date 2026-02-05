from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    # Article URLs
    path("articles/", views.ArticleListView.as_view(), name="article-list"),
    path("articles/create/", views.ArticleCreateView.as_view(), name="article-create"),
    path(
        "articles/<int:pk>/update/",
        views.ArticleUpdateView.as_view(),
        name="article-update",
    ),
    path(
        "articles/<int:pk>/delete/",
        views.ArticleDeleteView.as_view(),
        name="article-delete",
    ),
    # Category URLs
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path(
        "categories/create/", views.CategoryCreateView.as_view(), name="category-create"
    ),
    path(
        "categories/<int:pk>/update/",
        views.CategoryUpdateView.as_view(),
        name="category-update",
    ),
    path(
        "categories/<int:pk>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category-delete",
    ),
    # Tag URLs
    path("tags/", views.TagListView.as_view(), name="tag-list"),
    path("tags/create/", views.TagCreateView.as_view(), name="tag-create"),
    path("tags/<int:pk>/update/", views.TagUpdateView.as_view(), name="tag-update"),
    path("tags/<int:pk>/delete/", views.TagDeleteView.as_view(), name="tag-delete"),
    # Comment URLs
    path("comments/", views.CommentListView.as_view(), name="comment-list"),
    path(
        "comments/<int:pk>/update/",
        views.CommentUpdateView.as_view(),
        name="comment-update",
    ),
    path(
        "comments/<int:pk>/delete/",
        views.CommentDeleteView.as_view(),
        name="comment-delete",
    ),
]
