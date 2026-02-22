from django.db import models
from django.utils import timezone
from apps.users.models import User
# Create your models here.


# Dentist Profile
class DentistProfile(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    specialty = models.CharField(max_length=100, null=True)
    about_me = models.TextField(null=True)
    years_of_experience = models.IntegerField(null=True)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=11, null=True)

    def __str__(self):
        return self.user_id.username if self.user_id.username else "Dentist Profile"

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


# Service
# class Service(models.Model):
#     dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
#     name = models.CharField(max_length=150, null=True)
#     description = models.TextField(null=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
#     duration_minutes = models.IntegerField(null=True)
#     def __str__(self):
#         return self.name if self.name else "Service"


# Appointment
class Appointment(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    duration = models.TimeField(null=True)
    notes = models.TextField(null=True)
    status = models.CharField(max_length=20, null=True)
    way_of_communication = models.CharField(max_length=20, null=True)
    def __str__(self):
        return self.patient.username if self.patient and self.patient.username else "Appointment"

# Gallery
class Gallery(models.Model):
    dentist_id = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, null=True)
    image = models.URLField(null=True)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.image if self.image else "Gallery"
#
#
#67 