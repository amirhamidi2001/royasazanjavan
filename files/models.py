from django.db import models


class ExcelFile(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="excel_files/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Excelfile"
        verbose_name_plural = "Excelfiles"
        ordering = ["created_at"]

    def __str__(self):
        return self.title
