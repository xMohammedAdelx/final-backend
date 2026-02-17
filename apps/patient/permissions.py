from rest_framework import permissions
from apps.patient.models import PatientDoctorRelationship


class IsPatientOwner(permissions.BasePermission):
    """
    Custom permission to allow patients and staff/admin to view/edit/create their own profile
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        return obj.user_id == request.user


class CanAccessMedicalRecord(permissions.BasePermission):
    """
    Custom permission to allow patients, staff/admin and their doctor to view their own medical records
    """
    def has_object_permission(self, request, view, obj):
        # obj is a MedicalRecord instance
        user = request.user
        # If user is superuser, allow access
        if user.is_superuser:
            return True
        # Check if user is the patient
        if obj.patient_id and obj.patient_id.user_id == user:
            return True
        # Check if user is the treating dentist
        if obj.doctor_id and obj.doctor_id.user_id == user:
            return True
        return False


class CanAccessPrescription(permissions.BasePermission):
    """
    Custom permission to allow patients, admin and their doctor to view their own prescriptions
    """
    def has_object_permission(self, request, view, obj):
        # obj is a Prescription instance
        user = request.user
        # If user is superuser, allow access
        if user.is_superuser:
            return True
        # Get the medical record associated with this prescription
        medical_record = obj.medical_record
        if medical_record:
            # Check if user is the patient
            if medical_record.patient_id and medical_record.patient_id.user_id == user:
                return True
            # Check if user is the prescribing doctor
            if medical_record.doctor_id and medical_record.doctor_id.user_id == user:
                return True
        return False


class CanAccessPatientFullHistory(permissions.BasePermission):
    """
    Custom permission to allow patients, admin and their assigned doctors 
    to view the full patient history
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        elif obj.user_id == request.user:
            return True
        elif PatientDoctorRelationship.objects.filter(patient_id=obj, doctor_id__user_id=user, status="active").exists():
            return True
        else:
            return False


class CanManageDoctorAssignment(permissions.BasePermission):
    """
    Custom permission for managing patient-doctor relationships
    Patients can create and view their own assignments
    Doctors can view assignments where they are involved
    Staff/Admin can manage all assignments
    """
    def has_permission(self, request, view):
        # Called on EVERY request (including create)
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == "POST":
            return True
        return True

    def has_object_permission(self, request, view, obj):
        # Called only when accessing a specific object
        user = request.user
        if user.is_superuser:
            return True
        if request.method in permissions.SAFE_METHODS:
            if (obj.patient_id and obj.patient_id.user_id == user) or (
                obj.doctor_id and obj.doctor_id.user_id == user
            ):
                return True
            return False
        if request.method == "DELETE":
            return False
        # haven't decided yet to allow patient to manage their own doctor assignment or not
        # if request.method in ["PUT", "PATCH"]:
        #     if obj.patient_id and obj.patient_id.user_id == user:
        #         return True
        #     return False
        return False
