from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import ExcelFile


@login_required
def file_list(request):
    files = ExcelFile.objects.all().order_by("-created_at")
    return render(request, "files/file_list.html", {"files": files})


@login_required
def download_file(request, file_id):
    try:
        file_obj = ExcelFile.objects.get(id=file_id)
        response = FileResponse(
            file_obj.file, as_attachment=True, filename=file_obj.file.name
        )
        return response
    except ExcelFile.DoesNotExist:
        raise Http404("فایل مورد نظر یافت نشد.")
