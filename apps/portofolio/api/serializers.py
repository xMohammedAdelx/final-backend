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
            'about_me',
            'years_of_experience',
            'profile_image',
            'phone_number'
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


# class ServiceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Service
#         fields = ['id',
#         'dentist_id',
#         'name',
#         'description',
#         'price',
#         'duration_minutes',
#         ]
#         read_only_fields = ['id', 'dentist_id']

#     def validate_price(self, value):
#         if value is not None and value < 0:
#             raise serializers.ValidationError("Price cannot be negative.")
#         return value

#     def validate_duration_minutes(self, value):
#         if value is not None and value <= 0:
#              raise serializers.ValidationError("Duration must be a positive integer.")
#         return value

#     def validate_name(self, value):
#          if value and (len(value) < 2 or len(value) > 150):
#              raise serializers.ValidationError("Service name must be between 2 and 150 characters long.")
#          return value
#     def validate_description(self, value):
#          if value and (len(value) < 2 or len(value) > 255):
#              raise serializers.ValidationError("Service description must be between 2 and 255 characters long.")
#          return value



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
        if value < timezone.now().time():
             raise serializers.ValidationError("Appointment time must be in the future.")
        return value

    def validate_notes(self, value):
         if value and (len(value) < 2 or len(value) > 255):
             raise serializers.ValidationError("Appointment notes must be between 2 and 255 characters long.")
         return value    
    def validate_status(self, value):
         if value and (value not in ["upcoming", "completed", "cancelled"]):
             raise serializers.ValidationError("Appointment status must be upcoming or completed or cancelled.")
         return value    
    def validate_way_of_communication(self, value):
         if value and (value not in ["Messaging", "Voice Call", "Video Call"]):
             raise serializers.ValidationError("Appointment way of communication must be Messaging or Voice Call or Video Call.")
         return value    
    def validate_duration(self, value):
         if value and (value <= 0 ):
             raise serializers.ValidationError("Appointment duration must be a positive integer.")
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
