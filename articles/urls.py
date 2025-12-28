from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.ArticleListView.as_view(), name="article_list"),
    path("search/", views.ArticleSearchView.as_view(), name="article_search"),
    path(
        "category/<slug:slug>/",
        views.CategoryArticleListView.as_view(),
        name="category_list",
    ),
    path("tag/<slug:slug>/", views.TagArticleListView.as_view(), name="tag_list"),
    path(
        "author/<int:author_id>/",
        views.AuthorArticleListView.as_view(),
        name="author_list",
    ),
    path("<slug:slug>/", views.ArticleDetailView.as_view(), name="article_detail"),
]
