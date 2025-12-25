from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView

from .forms import (
    ConsultationRequestForm,
    ContactForm,
    JobApplicationForm,
)
from .models import ConsultationRequest, JobApplication


class IndexView(TemplateView):
    template_name = "website/index.html"


class AboutView(TemplateView):
    template_name = "website/about.html"


class FAQView(TemplateView):
    template_name = "website/faq.html"


class TosView(TemplateView):
    template_name = "website/tos.html"


class PageNotFoundView(TemplateView):
    template_name = "website/404.html"


class ContactView(FormView):
    """Handles display and processing of the contact form."""

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
    """Handles job application submissions."""

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
    """Handles consultation request submissions."""

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
