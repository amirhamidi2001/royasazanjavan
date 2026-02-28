from django.urls import path
from . import views

app_name = "files"

urlpatterns = [
    path("excelfiles/", views.ExcelFileListView.as_view(), name="excelfile-list"),
    path(
        "excelfiles/create/",
        views.ExcelFileCreateView.as_view(),
        name="excelfile-create",
    ),
    path(
        "excelfiles/<int:pk>/edit/",
        views.ExcelFileUpdateView.as_view(),
        name="excelfile-update",
    ),
    path(
        "excelfiles/<int:pk>/delete/",
        views.ExcelFileDeleteView.as_view(),
        name="excelfile-delete",
    ),
]
