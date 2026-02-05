# dashboard/templatetags/course_extras.py
from django import template

register = template.Library()


@register.filter
def completed_courses(courses):
    return sum(
        1
        for item in courses
        if item.progress and item.progress.completion_percentage == 100
    )
