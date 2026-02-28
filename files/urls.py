from django.urls import path
from . import views

app_name = "files"

urlpatterns = [
    path("", views.file_list, name="excelfile-list"),
    path("download/<int:file_id>/", views.download_file, name="download"),
]
