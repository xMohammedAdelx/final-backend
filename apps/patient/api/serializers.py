from rest_framework import serializers
from django.utils import timezone
from apps.patient.models import (
    PatientProfile, 
    MedicalRecord, 
    MedicalAttachment, 
    PatientDoctorRelationship,
    AIResult
)
from apps.portofolio.models import DentistProfile

class DoctorSummarySerializer(serializers.ModelSerializer):
    """
    Serializer to display basic doctor info in patient history.
    """
    first_name = serializers.CharField(source='user_id.first_name', read_only=True)
    last_name = serializers.CharField(source='user_id.last_name', read_only=True)
    
    class Meta:
        model = DentistProfile
        fields = ['id', 'first_name', 'last_name', 'specialty']

class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = '__all__'
        read_only_fields = ['id', 'user_id', 'created_at']

    def validate_name(self, value):
        if value and (len(value) < 2):
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        if value and not value.replace(" ", "").isalpha():
             raise serializers.ValidationError("Name must contain only letters and spaces.")
        return value

    def validate_phone(self, value):
        if value and (not value.isdigit() or len(value) != 11):
            raise serializers.ValidationError("Phone number must contain only digits and be 11 characters long.")
        return value

    def validate_date_of_birth(self, value):
        if value and value >= timezone.now().date():
            raise serializers.ValidationError("Date of birth must be in the past.")
        return value

    def validate_gender(self, value):
        if value and value not in ["male", "female", "M", "F", "Male", "Female"]:
            raise serializers.ValidationError("Gender must be either 'male' or 'female'.")
        return value



class MedicalAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalAttachment
        fields = '__all__'
        read_only_fields = ['id', 'uploaded_at']

    def validate_file(self, value):
        if value == " " or value == None:
            raise serializers.ValidationError("Attachment is required.")
        return value

class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def validate_date(self, value):
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Medical record date cannot be in the future.")
        return value

    def validate_diagnosis(self, value):
        if value and (len(value) < 3 or len(value) > 255):
            raise serializers.ValidationError("Diagnosis must be at least 3 characters long and less than 255 characters.")
        return value

    def validate_treatment(self, value):
        if value and (len(value) < 3 or len(value) > 255):
            raise serializers.ValidationError("Treatment must be at least 3 characters long and less than 255 characters.")
        return value

class AIResultSerializer(serializers.ModelSerializer):
    severity = serializers.SerializerMethodField()

    class Meta:
        model = AIResult
        fields = ['id', 'predicted_class', 'confidence_score', 'probabilities', 'created_at', 'description', 'suggestion', 'severity']
        read_only_fields = ['id', 'patient', 'created_at']

    def get_severity(self, obj):
        if not obj.predicted_class:
            return "green"
            
        predicted_class_lower = obj.predicted_class.lower()
        if "caries" in predicted_class_lower:
            return "red"
        elif "ulcer" in predicted_class_lower:
            return "yellow"
        elif "calculus" in predicted_class_lower:
            return "yellow"
        elif "gingivitis" in predicted_class_lower:
            return "yellow"
        elif "hypodontia" in predicted_class_lower:
            return "yellow"
        elif "discoloration" in predicted_class_lower:
            return "yellow"
            
        return "green"

class PatientDoctorRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDoctorRelationship
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def validate_status(self, value):
        if value and value not in ["active", "inactive", "pending", "Active", "Inactive", "Pending"]:
            raise serializers.ValidationError("Status must be either 'active' or 'inactive'.")
        return value

class MedicalRecordDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for medical records, including prescriptions and attachments.
    """
    ai_result = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalRecord
        fields = '__all__'
    
    def get_ai_result(self, obj):
        if obj.ai_result is None:
            return None
        return AIResultSerializer(obj.ai_result).data

    def get_attachments(self, obj):
        items = MedicalAttachment.objects.filter(medical_record=obj)
        return MedicalAttachmentSerializer(items, many=True).data

class PatientFullHistorySerializer(serializers.Serializer):
    patient = serializers.SerializerMethodField()
    assigned_doctors = serializers.SerializerMethodField()
    medical_records = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()

    def get_patient(self, obj):
        return PatientProfileSerializer(obj).data

    def get_assigned_doctors(self, obj):
        relationships = PatientDoctorRelationship.objects.filter(
            patient_id=obj, status="active"
        )
        doctors = []
        for rel in relationships:
            if rel.doctor_id:
                doctor_data = DoctorSummarySerializer(rel.doctor_id).data
                doctor_data["assigned_date"] = rel.assigned_date
                doctors.append(doctor_data)
        return doctors

    def get_medical_records(self, obj):
        records = MedicalRecord.objects.filter(patient_id=obj).order_by("-created_at")
        return MedicalRecordDetailSerializer(records, many=True).data

    def get_summary(self, obj):
        records = MedicalRecord.objects.filter(patient_id=obj)
        dates = records.values_list("created_at", flat=True)
        dates = [d.date() if d else None for d in dates if d is not None]

        return {
            "total_visits": records.count(),
            "first_visit": min(dates) if dates else None,
            "last_visit": max(dates) if dates else None,
        }
