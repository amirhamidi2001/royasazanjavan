from django.db import models


class ConsultationRequest(models.Model):
    """Stores consultation request submissions from users."""

    CONSULTATION_CHOICES = [
        ("online", "آنلاین"),
        ("in_person", "حضوری"),
        ("phone", "تلفنی"),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    consultation_type = models.CharField(
        max_length=20,
        choices=CONSULTATION_CHOICES,
    )
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.subject}"


class Contact(models.Model):
    """Represents a contact form submission."""

    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

    def __str__(self) -> str:
        return self.name


class JobApplication(models.Model):
    """Stores job application submissions."""

    GENDER_CHOICES = [
        ("male", "مذکر"),
        ("female", "مونث"),
    ]

    MARITAL_STATUS_CHOICES = [
        ("single", "مجرد"),
        ("married", "متاهل"),
    ]

    EDUCATION_CHOICES = [
        ("diploma", "دیپلم"),
        ("associate", "فوق دیپلم"),
        ("bachelor", "لیسانس"),
        ("master", "فوق لیسانس"),
        ("phd", "دکتری"),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=11)
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
    )
    education = models.CharField(
        max_length=20,
        choices=EDUCATION_CHOICES,
    )
    marital_status = models.CharField(
        max_length=10,
        choices=MARITAL_STATUS_CHOICES,
    )
    software_skills = models.CharField(max_length=255)
    resume = models.FileField(upload_to="resumes/")
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.subject}"


class Newsletter(models.Model):
    """Represents a newsletter subscription."""

    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"

    def __str__(self) -> str:
        return self.email
