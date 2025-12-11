from rest_framework import serializers
from apps.portofolio.models import *

class DentistProfileSerializer(serializers.ModelSerializer):
    # Add read-only display fields for dentist name
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

    def validate_rating(self, value):
        '''Ensure rating is between 1-5'''
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
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


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id',
        'dentist_id',
        'name',
        'category',
        ]
        read_only_fields = ['id', 'dentist_id']

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


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id',
        'dentist_id',
        'title',
        'content',
        ]
        read_only_fields = ['id', 'dentist_id']

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


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id',
        'dentist_id',
        'question',
        'answer',
        ]
        read_only_fields = ['id', 'dentist_id']

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
