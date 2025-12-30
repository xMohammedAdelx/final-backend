from rest_framework import serializers
from django.utils import timezone
from apps.portofolio.models import *

class DentistProfileSerializer(serializers.ModelSerializer):
    dentist_username = serializers.CharField(source='user_id.username', read_only=True)
    dentist_first_name = serializers.CharField(source='user_id.first_name', read_only=True)
    dentist_last_name = serializers.CharField(source='user_id.last_name', read_only=True)
    dentist_email = serializers.EmailField(source='user_id.email', read_only=True)
    class Meta:
        model = DentistProfile
        fields = [
            'id',
            'user_id',
            'dentist_username',
            'dentist_first_name',
            'dentist_last_name',
            'dentist_email',
            'specialty',
            'bio',
            'years_of_experience',
            'clinic_name',
            'clinic_address',
            'profile_image',
            'phone_number',
            'website',
        ]
        read_only_fields = ['id', 'dentist_username', 'dentist_first_name', 'dentist_last_name', 'dentist_email']

    def validate_years_of_experience(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative.")
        if value is not None and value > 100:
            raise serializers.ValidationError("Years of experience cannot be greater than 100.")
        return value

    def validate_phone_number(self, value):
        if value and (not value.isdigit() or len(value) != 11):
            raise serializers.ValidationError("Phone number must contain only digits and be 11 characters long.")
        return value

    def validate_clinic_name(self, value):
        if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Clinic name must be at least 2 characters long.")
        return value

    def validate_clinic_address(self, value):
        if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Clinic address must be at least 2 characters long.")
        return value

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = [
            'id',
            'dentist_id',
            'title',
            'Organization',
            'start_date',
            'end_date',
            'description',
        ]
        read_only_fields = ['id', 'dentist_id']

    def validate_dates(self, data):
        if 'start_date' in data and 'end_date' in data and data['end_date']:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("End date must be after start date.")
        return data

    def validate_title(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Title must be at least 2 characters long.")
         return value

    def validate_Organization(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Organization must be at least 2 characters long.")
         return value


class TestimonialSerializer(serializers.ModelSerializer):
    # Add read-only display fields
    patient_username = serializers.CharField(source='patient.username', read_only=True)
    dentist_name = serializers.CharField(
        source='dentist_id.user_id.username', read_only=True
    )

    class Meta:
        model = Testimonial
        fields = [
            'id',
            'dentist_id',
            'dentist_name',
            'patient',
            'patient_username',
            'patient_name',
            'feedback',
            'rating',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'patient',
            'patient_username',
            'dentist_name',
            'patient_name',
            'created_at',
        ]
    
    def validate_patient_name(self, value):
            if value.isalpha() and (len(value) < 2 or len(value) > 100):
                raise serializers.ValidationError("Patient name must be at least 2 characters long.")
            return value
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value
    
    def validate_feedback(self, value):
        if value and (len(value) < 2 or len(value) > 255):
            raise serializers.ValidationError("Feedback must be at least 2 characters long.")
        return value

    
class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ['id',
        'dentist_id', 
        'platform', 
        'url',
        ]
        read_only_fields = ['id', 'dentist_id']
    def validate_platform(self, value):
        if value and (len(value) < 2 or len(value) > 150):
            raise serializers.ValidationError("Platform must be at least 2 characters long.")
        return value
    def validate_url(self, value):
        if value and (len(value) < 2 or len(value) > 255):
            raise serializers.ValidationError("URL must be at least 2 characters long.")
        return value

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id',
        'dentist_id',
        'degree',
        'institution',
        'year',
        ]
        read_only_fields = ['id', 'dentist_id']

    def validate_year(self, value):
        current_year = timezone.now().year
        if value and (value < 1900 or value > current_year + 5):
             raise serializers.ValidationError("Invalid year.")
        return value

    def validate_degree(self, value):
         if value and len(value) < 2:
             raise serializers.ValidationError("Degree must be at least 2 characters long.")
         return value

    def validate_institution(self, value):
         if value and len(value) < 2:
             raise serializers.ValidationError("Institution must be at least 2 characters long.")
         return value


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id',
        'dentist_id',
        'name',
        'category',
        ]
        read_only_fields = ['id', 'dentist_id']

    def validate_name(self, value):
        if value and (len(value) < 2 or len(value) > 50):
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value
    
    def validate_category(self, value):
        if value and (len(value) < 2 or len(value) > 50):
            raise serializers.ValidationError("Category must be at least 2 characters long.")
        return value

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id',
        'dentist_id',
        'name',
        'description',
        'price',
        'duration_minutes',
        ]
        read_only_fields = ['id', 'dentist_id']

    def validate_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_duration_minutes(self, value):
        if value is not None and value <= 0:
             raise serializers.ValidationError("Duration must be a positive integer.")
        return value

    def validate_name(self, value):
         if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Service name must be between 2 and 150 characters long.")
         return value
    def validate_description(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Service description must be between 2 and 255 characters long.")
         return value


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id',
        'dentist_id',
        'title',
        'content',
        ]
        read_only_fields = ['id', 'dentist_id']
    
    def validate_title(self, value):
         if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Article title must be between 2 and 150 characters long.")
         return value
    
    def validate_content(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Article content must be between 2 and 255 characters long.")
         return value

class AwardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Awards
        fields = ['id',
        'dentist_id',
        'title',
        'description',
        'date',
        'image',
        ]
        read_only_fields = ['id', 'dentist_id']

    def validate_title(self, value):
         if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Award title must be between 2 and 150 characters long.")
         return value
    
    def validate_description(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Award description must be between 2 and 255 characters long.")
         return value

    def validate_date(self, value):
         if value and (value > timezone.now().date()):
             raise serializers.ValidationError("Award date must be in the past.")
         return value


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id',
        'dentist_id',
        'patient',
        'date',
        'time',
        'notes',
        'status',
        ]
        read_only_fields = ['id', 'patient']

    def validate_date(self, value):
        if value and value < timezone.now().date():
             raise serializers.ValidationError("Appointment date must be in the future.")
        return value
        
    def validate_time(self, value):
        if value is None:
             raise serializers.ValidationError("Time is required.")
        return value
        if value < timezone.now().time():
             raise serializers.ValidationError("Appointment time must be in the future.")
        return value

    def validate_notes(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Appointment notes must be between 2 and 255 characters long.")
         return value    
    def validate_status(self, value):
         if value and (value not in ["pending", "confirmed", "cancelled"]):
             raise serializers.ValidationError("Appointment status must be between 2 and 255 characters long.")
         return value    

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id',
        'dentist_id',
        'name',
        'description',
        'image',
        ]
        read_only_fields = ['id', 'dentist_id']

    def validate_name(self, value):
         if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Project name must be between 2 and 150 characters long.")
         return value    
    
    def validate_description(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Project description must be between 2 and 255 characters long.")
         return value    

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id',
        'dentist_id',
        'question',
        'answer',
        ]
        read_only_fields = ['id', 'dentist_id']
    
    def validate_question(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("FAQ question must be between 2 and 150 characters long.")
         return value    
    
    def validate_answer(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("FAQ answer must be between 2 and 255 characters long.")
         return value    

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['id',
        'dentist_id',
        'image',
        'description',
        'created_at',
        ]
        read_only_fields = ['id', 'dentist_id', 'created_at']

    def validate_description(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Gallery description must be between 2 and 255 characters long.")
         return value    

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id',
        'dentist_id',
        'name',
        'issued_by',
        'issue_date',
        'expiry_date',
        'credential_url',
        'image',
        ]
        read_only_fields = ['id', 'dentist_id']
    
    def validate_name(self, value):
         if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Certification name must be between 2 and 150 characters long.")
         return value    
    
    def validate_issued_by(self, value):
         if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Certification issued by must be between 2 and 150 characters long.")
         return value    
    
    def validate_issue_date(self, value):
         if value and (value > timezone.now().date()):
             raise serializers.ValidationError("Certification issue date must be in the past.")
         return value    
    
    def validate_expiry_date(self, value):
         if value and (value < timezone.now().date()):
             raise serializers.ValidationError("Certification expiry date must be in the future.")
         return value    
    
    def validate_credential_url(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Certification credential URL must be between 2 and 255 characters long.")
         return value       

    dentist_username = serializers.CharField(source='user_id.username', read_only=True)
    dentist_first_name = serializers.CharField(source='user_id.first_name', read_only=True)
    dentist_last_name = serializers.CharField(source='user_id.last_name', read_only=True)
    dentist_email = serializers.EmailField(source='user_id.email', read_only=True)
    class Meta:
        model = DentistProfile
        fields = [
            'id',
            'user_id',
            'dentist_username',
            'dentist_first_name',
            'dentist_last_name',
            'dentist_email',
            'specialty',
            'bio',
            'years_of_experience',
            'clinic_name',
            'clinic_address',
            'profile_image',
            'phone_number',
            'website',
        ]
        read_only_fields = ['id', 'dentist_username', 'dentist_first_name', 'dentist_last_name', 'dentist_email']

<<<<<<< HEAD
=======
    def validate_years_of_experience(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative.")
        if value is not None and value > 100:
            raise serializers.ValidationError("Years of experience cannot be greater than 100.")
        return value

    def validate_phone_number(self, value):
        if value and (not value.isdigit() or len(value) != 11):
            raise serializers.ValidationError("Phone number must contain only digits and be 11 characters long.")
        return value

    def validate_clinic_name(self, value):
        if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Clinic name must be at least 2 characters long.")
        return value

    def validate_clinic_address(self, value):
        if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Clinic address must be at least 2 characters long.")
        return value

>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212
class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = [
            'id',
            'dentist_id',
            'title',
            'Organization',
            'start_date',
            'end_date',
            'description',
        ]
        read_only_fields = ['id', 'dentist_id']

<<<<<<< HEAD
=======
    def validate_dates(self, data):
        if 'start_date' in data and 'end_date' in data and data['end_date']:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("End date must be after start date.")
        return data

    def validate_title(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Title must be at least 2 characters long.")
         return value

    def validate_Organization(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Organization must be at least 2 characters long.")
         return value

>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212

class TestimonialSerializer(serializers.ModelSerializer):
    # Add read-only display fields
    patient_username = serializers.CharField(source='patient.username', read_only=True)
    dentist_name = serializers.CharField(
        source='dentist_id.user_id.username', read_only=True
    )

    class Meta:
        model = Testimonial
        fields = [
            'id',
            'dentist_id',
            'dentist_name',
            'patient',
            'patient_username',
            'patient_name',
            'feedback',
            'rating',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'patient',
            'patient_username',
            'dentist_name',
            'patient_name',
            'created_at',
        ]
<<<<<<< HEAD

    def validate_rating(self, value):
        '''Ensure rating is between 1-5'''
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value


=======
    
    def validate_patient_name(self, value):
            if value.isalpha() and (len(value) < 2 or len(value) > 100):
                raise serializers.ValidationError("Patient name must be at least 2 characters long.")
            return value
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value
    
    def validate_feedback(self, value):
        if value and (len(value) < 2 or len(value) > 255):
            raise serializers.ValidationError("Feedback must be at least 2 characters long.")
        return value

    
>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212
class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ['id',
        'dentist_id', 
        'platform', 
        'url',
        ]
        read_only_fields = ['id', 'dentist_id']
<<<<<<< HEAD
=======
    def validate_platform(self, value):
        if value and (len(value) < 2 or len(value) > 150):
            raise serializers.ValidationError("Platform must be at least 2 characters long.")
        return value
    def validate_url(self, value):
        if value and (len(value) < 2 or len(value) > 255):
            raise serializers.ValidationError("URL must be at least 2 characters long.")
        return value
>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id',
        'dentist_id',
        'degree',
        'institution',
        'year',
        ]
        read_only_fields = ['id', 'dentist_id']

<<<<<<< HEAD
=======
    def validate_year(self, value):
        current_year = timezone.now().year
        if value and (value < 1900 or value > current_year + 5):
             raise serializers.ValidationError("Invalid year.")
        return value

    def validate_degree(self, value):
         if value and len(value) < 2:
             raise serializers.ValidationError("Degree must be at least 2 characters long.")
         return value

    def validate_institution(self, value):
         if value and len(value) < 2:
             raise serializers.ValidationError("Institution must be at least 2 characters long.")
         return value

>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id',
        'dentist_id',
        'name',
        'category',
        ]
        read_only_fields = ['id', 'dentist_id']

<<<<<<< HEAD
=======
    def validate_name(self, value):
        if value and (len(value) < 2 or len(value) > 50):
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value
    
    def validate_category(self, value):
        if value and (len(value) < 2 or len(value) > 50):
            raise serializers.ValidationError("Category must be at least 2 characters long.")
        return value

>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id',
        'dentist_id',
        'name',
        'description',
        'price',
        'duration_minutes',
        ]
        read_only_fields = ['id', 'dentist_id']

<<<<<<< HEAD
=======
    def validate_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_duration_minutes(self, value):
        if value is not None and value <= 0:
             raise serializers.ValidationError("Duration must be a positive integer.")
        return value

    def validate_name(self, value):
         if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Service name must be between 2 and 150 characters long.")
         return value
    def validate_description(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Service description must be between 2 and 255 characters long.")
         return value

>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id',
        'dentist_id',
        'title',
        'content',
        ]
        read_only_fields = ['id', 'dentist_id']
<<<<<<< HEAD
=======
    
    def validate_title(self, value):
         if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Article title must be between 2 and 150 characters long.")
         return value
    
    def validate_content(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Article content must be between 2 and 255 characters long.")
         return value
>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212

class AwardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Awards
        fields = ['id',
        'dentist_id',
        'title',
        'description',
        'date',
        'image',
        ]
        read_only_fields = ['id', 'dentist_id']

<<<<<<< HEAD
=======
    def validate_title(self, value):
         if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Award title must be between 2 and 150 characters long.")
         return value
    
    def validate_description(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Award description must be between 2 and 255 characters long.")
         return value

    def validate_date(self, value):
         if value and (value > timezone.now().date()):
             raise serializers.ValidationError("Award date must be in the past.")
         return value

>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id',
        'dentist_id',
        'patient',
        'date',
        'time',
        'notes',
        'status',
        ]
        read_only_fields = ['id', 'patient']

<<<<<<< HEAD
=======
    def validate_date(self, value):
        if value and value < timezone.now().date():
             raise serializers.ValidationError("Appointment date must be in the future.")
        return value
        
    def validate_time(self, value):
        if value is None:
             raise serializers.ValidationError("Time is required.")
        return value
        if value < timezone.now().time():
             raise serializers.ValidationError("Appointment time must be in the future.")
        return value

    def validate_notes(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Appointment notes must be between 2 and 255 characters long.")
         return value    
    def validate_status(self, value):
         if value and (value not in ["pending", "confirmed", "cancelled"]):
             raise serializers.ValidationError("Appointment status must be between 2 and 255 characters long.")
         return value    
>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id',
        'dentist_id',
        'name',
        'description',
        'image',
        ]
        read_only_fields = ['id', 'dentist_id']

<<<<<<< HEAD
=======
    def validate_name(self, value):
         if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Project name must be between 2 and 150 characters long.")
         return value    
    
    def validate_description(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Project description must be between 2 and 255 characters long.")
         return value    
>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id',
        'dentist_id',
        'question',
        'answer',
        ]
        read_only_fields = ['id', 'dentist_id']
<<<<<<< HEAD
=======
    
    def validate_question(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("FAQ question must be between 2 and 150 characters long.")
         return value    
    
    def validate_answer(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("FAQ answer must be between 2 and 255 characters long.")
         return value    
>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['id',
        'dentist_id',
        'image',
        'description',
        'created_at',
        ]
        read_only_fields = ['id', 'dentist_id', 'created_at']

<<<<<<< HEAD
=======
    def validate_description(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Gallery description must be between 2 and 255 characters long.")
         return value    

>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212
class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id',
        'dentist_id',
        'name',
        'issued_by',
        'issue_date',
        'expiry_date',
        'credential_url',
        'image',
        ]
        read_only_fields = ['id', 'dentist_id']
<<<<<<< HEAD
=======
    
    def validate_name(self, value):
         if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Certification name must be between 2 and 150 characters long.")
         return value    
    
    def validate_issued_by(self, value):
         if value and (len(value) < 2 or len(value) > 150):
             raise serializers.ValidationError("Certification issued by must be between 2 and 150 characters long.")
         return value    
    
    def validate_issue_date(self, value):
         if value and (value > timezone.now().date()):
             raise serializers.ValidationError("Certification issue date must be in the past.")
         return value    
    
    def validate_expiry_date(self, value):
         if value and (value < timezone.now().date()):
             raise serializers.ValidationError("Certification expiry date must be in the future.")
         return value    
    
    def validate_credential_url(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Certification credential URL must be between 2 and 255 characters long.")
         return value       
>>>>>>> d9f6ecded56012b89a9525d89e2ce95d8ab9f212
