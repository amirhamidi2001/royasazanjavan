from django import template

from ..models import PartnerCompany, Students

register = template.Library()


@register.inclusion_tag("website/testimonials.html")
def show_partners():
    partners = PartnerCompany.objects.all().order_by("-created_at")
    return {"partners": partners}


@register.inclusion_tag("website/students.html")
def show_students():
    students = Students.objects.all().order_by("-created_at")
    return {"students": students}
