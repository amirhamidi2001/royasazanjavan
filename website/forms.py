from django import forms

from .models import (
    ConsultationRequest,
    Contact,
    JobApplication,
    Newsletter,
)


class ConsultationRequestForm(forms.ModelForm):
    """Form for handling consultation request submissions."""

    class Meta:
        model = ConsultationRequest
        fields = "__all__"


class ContactForm(forms.ModelForm):
    """Form for handling contact submissions."""

    class Meta:
        model = Contact
        fields = "__all__"


class JobApplicationForm(forms.ModelForm):
    """Form for handling job application submissions."""

    class Meta:
        model = JobApplication
        fields = "__all__"


class NewsletterForm(forms.ModelForm):
    """Form for handling newsletter subscriptions."""

    class Meta:
        model = Newsletter
        fields = ["email"]
