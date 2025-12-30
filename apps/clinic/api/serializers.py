from rest_framework import serializers
from django.utils import timezone
from apps.clinic.models import (
    ClinicProfile, 
    ClinicService, 
    ClinicDoctors, 
    ClinicGallery,
    ClinicReview, 
    ClinicAppointment, 
    ClinicWorkingHours,
    ClinicContactMessage
)

class ClinicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicProfile
        fields = '__all__'
    def validate_clinic_name(self, value):
        if value and (len(value) < 2 or len(value) > 255):
            raise serializers.ValidationError("Clinic name must be at least 2 characters long and less than 255 characters.")
        return value
    def validate_phone(self, value):
        if value and (not value.isdigit() or len(value) != 11):
            raise serializers.ValidationError("Phone number must contain only digits and be 11 characters long.")
        return value

    def validate_address(self, value):
        if value and len(value) < 5:
            raise serializers.ValidationError("Address must be at least 5 characters long.")
        return value


class ClinicServiceSerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 

    class Meta:
        model = ClinicService
        fields = '__all__'
    def validate_service_name(self, value):
        if value and (len(value) < 2 or len(value) > 255):
            raise serializers.ValidationError("Service name must be at least 2 characters long and less than 255 characters.")
        return value
        
    def validate_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value



class ClinicDoctorsSerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 

    class Meta:
        model = ClinicDoctors
        fields = '__all__'
    
    def validate_doctor_name(self, value):
        if value and (len(value) < 2 or len(value) > 255):
            raise serializers.ValidationError("Doctor name must be at least 2 characters long and less than 255 characters.")
        return value
    
    

class ClinicGallerySerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 

    class Meta:
        model = ClinicGallery
        fields = '__all__'
    
    def validate_title(self, value):
        if value and (len(value) < 2 or len(value) > 255):
            raise serializers.ValidationError("Title must be at least 2 characters long and less than 255 characters.")
        return value
    

class ClinicReviewSerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 
    patient_username = serializers.ReadOnlyField(source='patient.username') 

    class Meta:
        model = ClinicReview
        fields = '__all__'
    
    def validate_rating(self, value):
        if value and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate_comment(self, value):
        if value and (len(value) < 2 or len(value) > 255):
            raise serializers.ValidationError("Comment must be at least 2 characters long and less than 255 characters.")
        return value

class ClinicAppointmentSerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 
    doctor_name = serializers.ReadOnlyField(source='doctor_name.doc_name') 

    class Meta:
        model = ClinicAppointment
        fields = '__all__'
    
    def validate_patient_name(self, value):
        if value and (len(value) < 2 or len(value) > 255):
            raise serializers.ValidationError("Patient name must be at least 2 characters long and less than 255 characters.")
        return value
    
    def validate_patient_phone(self, value):
        if value and (not value.isdigit() or len(value) != 11):
            raise serializers.ValidationError("Patient phone number must contain only digits and be 11 characters long.")
        return value

    def validate_date(self, value):
        if value and value < timezone.now().date():
             raise serializers.ValidationError("Appointment date must be in the future.")
        return value
        
    def validate_time(self, value):
        if value is None:
             raise serializers.ValidationError("Time is required.")
        return value
    
    def validate_status(self, value):
        if value not in ['pending', 'confirmed', 'completed', 'cancelled']:
            raise serializers.ValidationError("Invalid status.")
        return value

class ClinicWorkingHoursSerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 

    class Meta:
        model = ClinicWorkingHours
        fields = '__all__'
    
    def validate_name(self, value):
        if value and (len(value) < 2 or len(value) > 255):
            raise serializers.ValidationError("Name must be at least 2 characters long and less than 255 characters.")
        return value

    def validate(self, data):
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("End time must be after start time.")
        return data

class ClinicContactMessageSerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 

    class Meta:
        model = ClinicContactMessage
        fields = '__all__'

    def validate_name(self, value):
        if value and (len(value) < 2 or len(value) > 255):
            raise serializers.ValidationError("Name must be at least 2 characters long and less than 255 characters.")
        return value

    def validate_message(self, value):
        if value and (len(value) < 2 or len(value) > 1000):
            raise serializers.ValidationError("Message must be at least 2 characters long.")
        return value

    def validate_email(self, value):
        if value == "" or value == None :
            raise serializers.ValidationError("Email is required.")
        return value