from django import template
from ..models import PartnerCompany

register = template.Library()


@register.inclusion_tag("website/testimonials.html")
def show_partners():
    partners = PartnerCompany.objects.all().order_by("-created_at")
    return {"partners": partners}
