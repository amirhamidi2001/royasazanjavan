from django import forms
from django.utils.translation import gettext_lazy as _
from courses.models import CourseRating


class CourseRatingForm(forms.ModelForm):
    """Form for submitting course ratings and feedback."""

    RATING_CHOICES = [
        (1, "1 ★"),
        (2, "2 ★★"),
        (3, "3 ★★★"),
        (4, "4 ★★★★"),
        (5, "5 ★★★★★"),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "rating-input"}),
        label=_("Rating"),
        help_text=_("Select your rating from 1 to 5 stars"),
    )

    feedback = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": _("Write your feedback about this course..."),
            }
        ),
        label=_("Feedback"),
        help_text=_("Share your experience with this course"),
    )

    class Meta:
        model = CourseRating
        fields = ["rating", "feedback"]

    def clean_rating(self):
        """Ensure rating is within the valid range."""
        rating = int(self.cleaned_data["rating"])
        if rating < 1 or rating > 5:
            raise forms.ValidationError(_("Rating must be between 1 and 5."))
        return rating

    def clean_feedback(self):
        """Validate feedback content."""
        feedback = self.cleaned_data["feedback"]
        if len(feedback) < 10:
            raise forms.ValidationError(
                _("Feedback must be at least 10 characters long.")
            )
        return feedback
