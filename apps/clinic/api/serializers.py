from rest_framework import serializers
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

class ClinicServiceSerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 

    class Meta:
        model = ClinicService
        fields = '__all__'

class ClinicDoctorsSerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 

    class Meta:
        model = ClinicDoctors
        fields = '__all__'

class ClinicGallerySerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 

    class Meta:
        model = ClinicGallery
        fields = '__all__'

class ClinicReviewSerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 
    patient_username = serializers.ReadOnlyField(source='patient.username') 

    class Meta:
        model = ClinicReview
        fields = '__all__'

class ClinicAppointmentSerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 
    doctor_name = serializers.ReadOnlyField(source='doctor_name.doc_name') 

    class Meta:
        model = ClinicAppointment
        fields = '__all__'

class ClinicWorkingHoursSerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 

    class Meta:
        model = ClinicWorkingHours
        fields = '__all__'

class ClinicContactMessageSerializer(serializers.ModelSerializer):
    clinic_name = serializers.ReadOnlyField(source='clinic.name') 

    class Meta:
        model = ClinicContactMessage
        fields = '__all__'

