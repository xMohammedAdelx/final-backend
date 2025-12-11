from django.db import models

from apps.users.models import User

# Create your models here.

# Clinic Profile
class ClinicProfile(models.Model):
    name = models.CharField(max_length=255, null=True)
    address = models.TextField(null=True)
    phone = models.CharField(max_length=255, null=True)    
    email = models.EmailField(null=True)
    description = models.TextField(null=True)
    website = models.URLField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


# Clinic Service
class ClinicService(models.Model):
    clinic = models.ForeignKey(ClinicProfile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True , null=True)
    def __str__(self):
        return self.name

# Clinic Doctors
class ClinicDoctors(models.Model):
    clinic = models.ForeignKey(ClinicProfile, on_delete=models.CASCADE, null=True)
    doc_name = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.doc_name


# Clinic Gallery
class ClinicGallery(models.Model):
    clinic = models.ForeignKey(ClinicProfile, on_delete=models.CASCADE, null=True)
    image = models.URLField(null=True)
    description = models.TextField(null=True)
    title = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.title


# Clinic Review
class ClinicReview(models.Model):
    clinic = models.ForeignKey(ClinicProfile, on_delete=models.CASCADE, null=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(null=True)
    comment = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        if self.patient:
            return f"{self.patient.username}'s review"
        return "Anonymous review"


# Clinic Appointment
class ClinicAppointment(models.Model):
    clinic = models.ForeignKey(ClinicProfile, on_delete=models.CASCADE , null=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    patient_name = models.CharField(max_length=255, null=True)
    patient_phone = models.CharField(max_length=255, null=True)
    doctor_name = models.ForeignKey(ClinicDoctors, on_delete=models.CASCADE , null=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    notes = models.TextField(null=True)
    status_choices = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='pending')
    created_at = models.DateTimeField(auto_now_add=True , null=True)
    def __str__(self):
        return self.patient_name


# Clinic Working Hours
class ClinicWorkingHours(models.Model):
    clinic = models.ForeignKey(ClinicProfile, on_delete=models.CASCADE , null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    name = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.name


# Clinic Contact Message
class ClinicContactMessage(models.Model):
    clinic = models.ForeignKey(ClinicProfile, on_delete=models.CASCADE , null=True)
    name = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True)
    message = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.name
