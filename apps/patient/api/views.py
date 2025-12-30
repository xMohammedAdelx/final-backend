from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.patient.models import (
    AITreatmentSuggestion,
    PatientProfile,
    MedicalRecord,
    Prescription,
    PatientDoctorRelationship
    )
from apps.patient.api.serializers import (
    PatientProfileSerializer,
    MedicalRecordSerializer,
    PrescriptionSerializer,
    PatientDoctorRelationshipSerializer,
    PatientFullHistorySerializer,
    AITreatmentSuggestionSerializer
    )
from apps.patient.permissions import (
    IsPatientOwner,
    CanAccessMedicalRecord,
    CanAccessPrescription,
    CanAccessPatientFullHistory,
    CanManageDoctorAssignment
    )


class PatientProfileViewSet(viewsets.ModelViewSet):
    queryset = PatientProfile.objects.all()
    serializer_class = PatientProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name','phone','gender','address','date_of_birth']
    ordering_fields = ['name','phone','gender','address','date_of_birth','created_at']

    permission_classes = [permissions.IsAuthenticated, IsPatientOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return PatientProfile.objects.all()
        # Return only the patient profile belonging to this user
        return PatientProfile.objects.filter(user_id=user)

    def perform_create(self, serializer):
        # Automatically set the user_id to the requesting user when creating a profile
        serializer.save(user_id=self.request.user)

    @action(detail=True, methods=["get"])
    def medical_records(self, request, pk=None):
        patient = self.get_object()
        medical_records = MedicalRecord.objects.filter(patient_id=patient)
        serializer = MedicalRecordSerializer(medical_records, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def me(self, request):
        try:
            profile = PatientProfile.objects.get(user_id=request.user)
            serializer = PatientProfileSerializer(profile)
            return Response(serializer.data)
        except PatientProfile.DoesNotExist:
            return Response(
                {"detail": "No patient profile found for the current user."},
                status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=True, methods=["get"], 
        permission_classes=[permissions.IsAuthenticated, CanAccessPatientFullHistory]
    )
    def full_history(self, request, pk=None):
        patient = self.get_object()
        serializer = PatientFullHistorySerializer(patient)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_history(self, request):
        try:
            patient = PatientProfile.objects.get(user_id=request.user)
            serializer = PatientFullHistorySerializer(patient)
            return Response(serializer.data)
        except PatientProfile.DoesNotExist:
            return Response(
                {"detail": "No patient profile found for the current user."},
                status=status.HTTP_404_NOT_FOUND)

class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient_id','doctor_id','date','diagnosis','treatment','notes']
    ordering_fields = ["clinic", "doctor", "date", "created_at"]
    permission_classes = [permissions.IsAuthenticated, CanAccessMedicalRecord]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return MedicalRecord.objects.none()
        if user.is_superuser:
            return MedicalRecord.objects.all()
        try:
            if user.staff.is_active:
                return MedicalRecord.objects.filter(clinic=user.staff.clinic)
        except AttributeError:
            pass
        patient_records = MedicalRecord.objects.filter(patient_id__user_id=user)
        doctor_records = MedicalRecord.objects.filter(doctor_id__user_id=user)
        return (patient_records | doctor_records).distinct()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            # Only doctors and staff can modify medical records
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            # Anyone authenticated can view (filtered by get_queryset)
            permission_classes = [permissions.IsAuthenticated, CanAccessMedicalRecord]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        clinic = None
        try:
            if self.request.user.staff.is_active:
                clinic = self.request.user.staff.clinic
        except AttributeError:
            pass
        patient_id = self.request.data.get("patient")
        if not patient_id:
            # If patient is not provided, we can't create a record
            # But 'patient' is a required field on the model.
            # We should probably raise a validation error if it's missing from the request payload
            # even if the serializer ignores it due to read_only.

            raise ValidationError({"patient": "This field is required."})

        serializer.save(patient_id=patient_id, clinic=clinic)

    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        """
        Add a file URL attachment (e.g. S3 link) to a medical record.
        Better for speed and storage optimization.
        """
        record = self.get_object()
        file_url = request.data.get('file_url')
        description = request.data.get('description', '')

        if not file_url:
            return Response({"detail": "No file_url provided."}, status=status.HTTP_400_BAD_REQUEST)

        attachment = MedicalAttachment.objects.create(
            record=record,
            file_url=file_url,
            description=description
        )
        return Response(
            MedicalAttachmentSerializer(attachment).data, 
            status=status.HTTP_201_CREATED
        )
    @action(detail=True, methods=["get"])
    def prescriptions(self, request, pk=None):
        medical_record = self.get_object()
        prescriptions = Prescription.objects.filter(medical_record=medical_record)
        serializer = PrescriptionSerializer(prescriptions, many=True)
        return Response(serializer.data)


class AITreatmentSuggestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AI Treatment Suggestions
    """
    serializer_class = AITreatmentSuggestionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["doctor_verdict", "created_at"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return AITreatmentSuggestion.objects.none()

        # Superuser sees all
        if user.is_superuser:
            return AITreatmentSuggestion.objects.all()

        # Staff sees suggestions for their clinic's patients or that they reviewed
        try:
            if user.staff.is_active:
                # This logic can be expanded based on specific needs
                # For now, let's allow staff to see all suggestions to facilitate review
                return AITreatmentSuggestion.objects.all()
        except AttributeError:
            pass

        # Patients see ONLY their own suggestions
        return AITreatmentSuggestion.objects.filter(patient=user)

    def perform_create(self, serializer):
        # Allow patients to create suggestions (trigger AI) or doctors
        # If user is patient, set patient field automatically
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            serializer.save(patient=self.request.user)
        else:
            # For staff/doctors, they must provide the patient ID in the request body
            # because 'patient' is read_only in the serializer.
            patient_id = self.request.data.get("patient")
            if not patient_id:
                from rest_framework.exceptions import ValidationError

                raise ValidationError(
                    {
                        "patient": "This field is required for staff creating suggestions."
                    }
                )

            serializer.save(patient_id=patient_id)

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        """
        Doctor reviews the AI suggestion.
        """
        suggestion = self.get_object()

        # Ensure only doctors/staff can review
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "Only doctors can review suggestions."},
                status=status.HTTP_403_FORBIDDEN,
            )

        verdict = request.data.get("verdict")
        notes = request.data.get("notes", "")

        if verdict not in ["approved", "rejected", "modified"]:
            return Response(
                {"detail": "Invalid verdict."}, status=status.HTTP_400_BAD_REQUEST
            )

        suggestion.doctor_verdict = verdict
        suggestion.doctor_notes = notes

        # Optionally link the doctor reviewing it
        try:
            # Assuming the staff member is a doctor.
            # You might need more specific logic to find the 'ClinicDoctors' instance
            # matching the logged-in staff user.
            # For now, we'll leave 'reviewed_by' null unless passed explicitly or logic added.
            pass
        except:
            pass

        suggestion.save()

        return Response(AITreatmentSuggestionSerializer(suggestion).data)


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['medical_record','medicine_name','dosage','duration','instructions','prescribed_date']
    ordering_fields = ['prescribed_date','created_at']

    permission_classes = [permissions.IsAuthenticated, CanAccessPrescription]

    def get_queryset(self):

        user = self.request.user

        if user.is_staff or user.is_superuser:
            return Prescription.objects.all()
        # Get prescriptions where user is the patient
        patient_prescriptions = Prescription.objects.filter(
            medical_record__patient_id__user_id=user
        )
        # Get prescriptions where user is the prescribing doctor
        doctor_prescriptions = Prescription.objects.filter(
            medical_record__doctor_id__user_id=user
        )
        return (patient_prescriptions | doctor_prescriptions).distinct()

    def get_permissions(self):

        if self.action in ["create", "update", "partial_update", "destroy"]:
            # Only doctors and staff can modify prescriptions
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            # Anyone authenticated can view (filtered by get_queryset)
            permission_classes = [permissions.IsAuthenticated, CanAccessPrescription]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["get"])
    def medical_record(self, request, pk=None):
        prescription = self.get_object()
        medical_record = MedicalRecord.objects.filter(prescription=prescription)
        serializer = MedicalRecordSerializer(medical_record, many=True)
        return Response(serializer.data)


class PatientDoctorRelationshipViewSet(viewsets.ModelViewSet):
    queryset = PatientDoctorRelationship.objects.all()
    serializer_class = PatientDoctorRelationshipSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageDoctorAssignment]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status"]
    ordering_fields = ["assigned_date", "created_at"]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return PatientDoctorRelationship.objects.all()
        patient_relationships = PatientDoctorRelationship.objects.filter(
            patient_id__user_id=user
        )
        doctor_relationships = PatientDoctorRelationship.objects.filter(
            doctor_id__user_id=user
        )
        return (patient_relationships | doctor_relationships).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        patient_id = serializer.validated_data.get("patient_id")
        # If patient_id is not provided, try to use the current user's patient profile
        if not patient_id:
            try:
                patient_profile = PatientProfile.objects.get(user_id=user)
                serializer.save(patient_id=patient_profile)
                return
            except PatientProfile.DoesNotExist:
                raise ValidationError(
                    {
                        "detail": "You must create a patient profile before assigning a doctor."
                    }
                )
        # Validate that user has permission to create this relationship
        if patient_id.user_id == user:
            # Patient creating their own assignment - allowed
            serializer.save()
        elif user.is_staff or user.is_superuser:
            # Admin creating - allowed
            serializer.save()
        else:
            raise ValidationError(
                {
                    "detail": "You can only create relationships for yourself."
                }
            )
