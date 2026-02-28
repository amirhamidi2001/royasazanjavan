from django.contrib import admin
from .models import ExcelFile


@admin.register(ExcelFile)
class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)
