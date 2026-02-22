from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView, View

from .forms import (
    ConsultationRequestForm,
    ContactForm,
    JobApplicationForm,
)
from .models import ConsultationRequest, JobApplication


class IndexView(TemplateView):
    """
    View for rendering the main landing page of the website.
    """

    template_name = "website/index.html"


class AboutView(TemplateView):
    """
    View for rendering the about us page with company information.
    """

    template_name = "website/about.html"


class FAQView(TemplateView):
    """
    View for rendering the frequently asked questions page.
    """

    template_name = "website/faq.html"


class TosView(TemplateView):
    """
    View for rendering the terms of service and legal agreement page.
    """

    template_name = "website/tos.html"


class PageNotFoundView(TemplateView):
    """
    View for rendering the 404 error page when a page is not found.
    """

    template_name = "website/404.html"


class ContactView(FormView):
    """
    Handles display and processing of the contact form.
    """

    template_name = "website/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("website:contact")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "پیام شما با موفقیت ارسال شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "ارسال پیام ناموفق بود.")
        return super().form_invalid(form)


class JobApplicationView(CreateView):
    """
    Handles job application submissions.
    """

    model = JobApplication
    form_class = JobApplicationForm
    template_name = "website/job_application.html"
    success_url = reverse_lazy("website:job-application")

    def form_valid(self, form):
        softwares = self.request.POST.getlist("software_skills")

        instance = form.save(commit=False)
        instance.software_skills = ", ".join(softwares)
        instance.save()

        messages.success(self.request, "اطلاعات شما با موفقیت ثبت شد.")
        return super().form_valid(form)


class SupportView(CreateView):
    """
    Handles consultation request submissions.
    """

    model = ConsultationRequest
    form_class = ConsultationRequestForm
    template_name = "website/support.html"
    success_url = reverse_lazy("website:support")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "اطلاعات شما با موفقیت ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "خطایی در ارسال فرم رخ داد. لطفا فیلدها را بررسی کنید.",
        )
        return super().form_invalid(form)


class Custom404View(View):
    """Custom 404 error page view."""

    template_name = "website/404.html"

    def get(self, request, exception=None):
        """Render the custom 404 page."""
        return render(request, self.template_name, status=404)


def ads_txt(request):
    content = """google.com, pub-1234567890123456, DIRECT, f08c47fec0942fa0"""
    return HttpResponse(content, content_type="text/plain")
