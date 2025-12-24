from rest_framework import serializers
from django.utils import timezone
from apps.patient.models import (
    PatientProfile,
    MedicalRecord,
    Prescription,
    PatientDoctorRelationship,
    MedicalAttachment,
    AITreatmentSuggestion
    )
from apps.portofolio.models import DentistProfile

class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = '__all__'
    
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



class DoctorSummarySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = DentistProfile
        fields = ["id", "name", "specialty", "clinic_name", "profile_image"]

    def get_name(self, obj):
        if obj.user_id:
            full_name = obj.user_id.get_full_name()
            if full_name.strip():
                return full_name
            return obj.user_id.username
        return "Unknown Doctor"

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'

    def validate_duration(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Duration must be a positive integer.")
        return value

    def validate_prescribed_date(self, value):
        if value and value > timezone.now().date():
             raise serializers.ValidationError("Prescribed date cannot be in the future.")
        return value

class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'

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


class AITreatmentSuggestionSerializer(serializers.ModelSerializer):
    reviewed_by_name = serializers.ReadOnlyField(source="reviewed_by.doc_name")

    class Meta:
        model = AITreatmentSuggestion
        fields = "__all__"
        read_only_fields = ["patient", "created_at", "updated_at"]

class MedicalAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalAttachment
        fields = "__all__"

    def validate_file(self, value):
        if value == " " or value == None:
            raise serializers.ValidationError("Attachment is required.")
        return value


class MedicalRecordDetailSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()
    prescriptions = serializers.SerializerMethodField()
    attachments = MedicalAttachmentSerializer(many=True, read_only=True)
    clinic_name = serializers.ReadOnlyField(source="clinic.name")
    doctor_name = serializers.ReadOnlyField(source="doctor.doc_name")
    ai_suggestion_details = AITreatmentSuggestionSerializer(
        source="ai_suggestion", read_only=True
    )
    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "patient_id",
            "doctor",
            "date",
            "diagnosis",
            "treatment",
            "notes",
            "prescriptions",
            "created_at",
        ]

    def get_doctor(self, obj):
        if obj.doctor_id:
            return DoctorSummarySerializer(obj.doctor_id).data
        return None
    def get_prescriptions(self, obj):
        prescriptions = Prescription.objects.filter(medical_record=obj)
        return PrescriptionSerializer(prescriptions, many=True).data


class PatientDoctorRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDoctorRelationship
        fields = "__all__"

    def validate_status(self, value):
        if value and value not in ["active", "inactive", "pending", "Active", "Inactive", "Pending"]:
             raise serializers.ValidationError("Status must be either 'active' or 'inactive'.")
        return value
    

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
        records = MedicalRecord.objects.filter(patient_id=obj).order_by("-date")
        return MedicalRecordDetailSerializer(records, many=True).data

    def get_summary(self, obj):
        records = MedicalRecord.objects.filter(patient_id=obj)
        total_prescriptions = Prescription.objects.filter(
            medical_record__patient_id=obj
        ).count()

        dates = records.values_list("date", flat=True)
        dates = [d for d in dates if d is not None]

        return {
            "total_visits": records.count(),
            "total_prescriptions": total_prescriptions,
            "first_visit": min(dates) if dates else None,
            "last_visit": max(dates) if dates else None,
        }
