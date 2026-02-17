from django.db import models
from django.utils import timezone
from apps.users.models import User
# Create your models here.


# Dentist Profile
class DentistProfile(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    specialty = models.CharField(max_length=100, null=True)
    bio = models.TextField(null=True)
    years_of_experience = models.IntegerField(null=True)
    clinic_name = models.CharField(max_length=150, null=True)
    clinic_address = models.CharField(max_length=255, null=True)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=11, null=True)
    website = models.URLField(null=True)
    def __str__(self):
        return self.user_id.username if self.user_id.username else "Dentist Profile"

# Experience
class Experience(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255, null=True)
    Organization = models.CharField(max_length=255, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True)
    def __str__(self):
        return self.title if self.title else "Experience"


# Testimonial
class Testimonial(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True, related_name="testimonials")
    patient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="testimonials_given")
    patient_name = models.CharField(max_length=100, null=True)
    feedback = models.TextField(null=True)
    rating = models.IntegerField(null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return (
            f"{self.patient_name} - {self.dentist_id}"
            if self.patient_name and self.dentist_id
            else "Testimonial")


# Social Media
class SocialMedia(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    platform = models.CharField(max_length=150, null=True)
    url = models.URLField(null=True)
    def __str__(self):
        return self.platform if self.platform else "Social Media"

# Education ***
class Education(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    degree = models.CharField(max_length=100, null=True)
    institution = models.CharField(max_length=100, null=True)
    year = models.IntegerField(null=True)  # Store just the year (e.g., 2020)
    def __str__(self):
        return self.degree if self.degree else "Education"

# Skill
class Skill(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50, null=True)
    category = models.CharField(max_length=50, null=True)
    def __str__(self):
        return self.name if self.name else "Skill"

# Service
class Service(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=150, null=True)
    description = models.TextField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    duration_minutes = models.IntegerField(null=True)
    def __str__(self):
        return self.name if self.name else "Service"


# Article ***
class Article(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255, null=True)
    content = models.TextField(null=True)
    image = models.URLField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.title if self.title else "Article"

# Awards ***
class Awards(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    date = models.DateField(null=True)
    image = models.URLField(null=True)
    def __str__(self):
        return self.title if self.title else "Awards"

# Appointment
class Appointment(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    notes = models.TextField(null=True)
    status = models.CharField(max_length=20, null=True)
    def __str__(self):
        return self.patient.username if self.patient and self.patient.username else "Appointment"

# Project ***
class Project(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=150, null=True)
    description = models.TextField(null=True)
    image = models.URLField(null=True)
    def __str__(self):
        return self.name if self.name else "Project"


# FAQ ***
class FAQ(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    question = models.CharField(max_length=255, null=True)
    answer = models.TextField(null=True)
    def __str__(self):
        return self.question if self.question else "FAQ"

# Gallery
class Gallery(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    image = models.URLField(null=True)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.image if self.image else "Gallery"

# Certification ***
class Certification(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=150, null=True)
    issued_by = models.CharField(max_length=150, null=True)
    issue_date = models.DateField(null=True)
    expiry_date = models.DateField(null=True)
    credential_url = models.URLField(null=True)
    image = models.URLField(null=True)
    def __str__(self):
        return self.name if self.name else "Certification"
