from django.db import models

# Create your models here.


# Dentist Profile
class DentistProfile(models.Model):
    pass


# Skill
class Skill(models.Model):
    pass


# Education
class Education(models.Model):
    pass


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


# Project
class Project(models.Model):
    pass


# Testimonial
class Testimonial(models.Model):
    pass

# FAQ
class FAQ(models.Model):
    pass


# Awards
class Awards(models.Model):
    pass


# Certification
class Certification(models.Model):
    pass


# Service
class Service(models.Model):
    pass


class SocialMedia(models.Model):
    pass

class Article(models.Model):
    pass


