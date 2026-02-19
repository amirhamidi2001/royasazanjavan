from django import template
from ..models import Course

register = template.Library()


@register.inclusion_tag("courses/latest_courses.html")
def show_latest_courses(count=8):
    """Fetches active courses, ordered by the most recent."""
    courses = Course.objects.filter(is_active=True).order_by("-created_date")[:count]
    return {"courses": courses}
