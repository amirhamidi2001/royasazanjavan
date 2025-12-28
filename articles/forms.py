from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    """
    Form used for submitting comments on articles.
    Includes custom validation for content, email, and website fields.
    """

    class Meta:
        """
        Meta configuration for CommentForm.
        Defines model binding, exposed fields, widgets,
        labels, and custom error messages.
        """

        model = Comment
        fields = ["name", "email", "website", "body"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "name",
                    "placeholder": "نام کامل خود را وارد کنید",
                    "required": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "id": "email",
                    "placeholder": "آدرس ایمیل خود را وارد کنید",
                    "required": True,
                }
            ),
            "website": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "id": "website",
                    "placeholder": "وبسایت شما (اختیاری)",
                }
            ),
            "body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "id": "comment",
                    "rows": 5,
                    "placeholder": "نظر خود را اینجا بنویسید...",
                    "required": True,
                }
            ),
        }
        labels = {
            "name": "نام کامل *",
            "email": "آدرس ایمیل *",
            "website": "وبسایت",
            "body": "نظر شما *",
        }
        error_messages = {
            "name": {
                "required": "لطفاً نام خود را وارد کنید",
                "max_length": "نام نباید بیشتر از 80 کاراکتر باشد",
            },
            "email": {
                "required": "لطفاً ایمیل خود را وارد کنید",
                "invalid": "لطفاً یک آدرس ایمیل معتبر وارد کنید",
            },
            "body": {
                "required": "لطفاً متن کامنت خود را وارد کنید",
            },
        }

    def clean_body(self):
        """
        Validate the comment body content.
        Enforces minimum and maximum length
        and performs basic spam detection.
        """
        body = self.cleaned_data.get("body")

        if body:
            # Enforce minimum comment length
            if len(body) < 10:
                raise forms.ValidationError("کامنت شما باید حداقل 10 کاراکتر باشد.")

            # Enforce maximum comment length
            if len(body) > 1000:
                raise forms.ValidationError(
                    "کامنت شما نباید بیشتر از 1000 کاراکتر باشد."
                )

            # Basic spam keyword detection
            spam_words = ["spam", "viagra", "casino"]
            if any(word in body.lower() for word in spam_words):
                raise forms.ValidationError("محتوای نامناسب شناسایی شد.")

        return body

    def clean_email(self):
        """
        Validate the email field.
        Blocks known temporary or disposable email domains.
        """
        email = self.cleaned_data.get("email")

        # List of blocked disposable email domains
        blocked_domains = ["tempmail.com", "throwaway.email"]
        domain = email.split("@")[1] if "@" in email else ""

        if domain in blocked_domains:
            raise forms.ValidationError("لطفاً از یک ایمیل معتبر استفاده کنید.")

        return email

    def clean_website(self):
        """
        Normalize and validate the website URL.
        Automatically prepends HTTPS if missing.
        """
        website = self.cleaned_data.get("website")

        if website:
            # Ensure the URL starts with http or https
            if not website.startswith(("http://", "https://")):
                website = "https://" + website

        return website
