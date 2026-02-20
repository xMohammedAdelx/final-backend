from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from apps.patient.api.services import get_ai_prediction
from apps.patient.models import (
    AIResult,
    PatientProfile,
    MedicalRecord,
    MedicalAttachment,
    PatientDoctorRelationship
    )
from apps.patient.api.serializers import (
    PatientProfileSerializer,
    MedicalRecordSerializer,
    MedicalAttachmentSerializer,
    PatientDoctorRelationshipSerializer,
    PatientFullHistorySerializer,
    AIResultSerializer
    )
from apps.patient.permissions import (
    IsPatientOwner,
    CanAccessMedicalRecord,
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
    search_fields = ['patient_id','ai_result','created_at','updated_at']
    ordering_fields = ["patient_id", "ai_result", "created_at", "updated_at"]
    permission_classes = [permissions.IsAuthenticated, CanAccessMedicalRecord]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return MedicalRecord.objects.none()
        if user.is_superuser:
            return MedicalRecord.objects.all()

        patient_records = MedicalRecord.objects.filter(patient_id__user_id=user)
        return patient_records

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            # Only doctors and staff can modify medical records
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            # Anyone authenticated can view (filtered by get_queryset)
            permission_classes = [permissions.IsAuthenticated, CanAccessMedicalRecord]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        patient_profile_id = self.request.data.get("patient_id") or self.request.data.get("patient")
        if not patient_profile_id:
            raise ValidationError({"patient_id": "This field is required."})

        patient_profile = PatientProfile.objects.filter(pk=patient_profile_id).first()
        if not patient_profile:
            raise ValidationError({"patient_id": "Invalid patient profile."})
        if not patient_profile.user_id:
            raise ValidationError({"patient_id": "Patient profile has no linked user."})

        ai_result = AIResult.objects.create(
            patient=patient_profile.user_id,
            prediction=self.request.data.get("prediction"),
            confidence_score=self.request.data.get("confidence_score"),
            probabilities=self.request.data.get("probabilities")
        )
        serializer.save(patient_id=patient_profile, ai_result=ai_result)

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
            medical_record=record,
            file_url=file_url,
            description=description
        )
        return Response(
            MedicalAttachmentSerializer(attachment).data, 
            status=status.HTTP_201_CREATED
        )


class AIResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AI Results
    """
    serializer_class = AIResultSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["predicted_class", "confidence_score", "created_at"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return AIResult.objects.none()

        # Superuser sees all
        if user.is_superuser:
            return AIResult.objects.all()



        # Patients see ONLY their own results
        return AIResult.objects.filter(patient=user)

    def perform_create(self, serializer):
        # Allow patients to create results (trigger AI) or doctors
        # If user is patient, set patient field automatically
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            serializer.save(patient=self.request.user)
        else:
            # For staff/doctors, they must provide the patient ID in the request body
            # because 'patient' is read_only in the serializer.
            patient_id = self.request.data.get("patient")
            if not patient_id:
                raise ValidationError(
                    {
                        "patient": "This field is required for staff creating results."
                    }
                )

            serializer.save(patient_id=patient_id)

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        """
        Doctor reviews the AI result.
        """
        result = self.get_object()

        # Ensure only doctors/staff can review
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "Only doctors can review results."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Optionally link the doctor reviewing it
        try:
            # Assuming the staff member is a doctor.
            # You might need more specific logic to find the 'ClinicDoctors' instance
            # matching the logged-in staff user.
            # For now, we'll leave 'reviewed_by' null unless passed explicitly or logic added.
            pass
        except:
            pass

        result.save()

        return Response(AIResultSerializer(result).data)

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
class AnalyzeDentalImageView(APIView):
    """
    Upload a dental image, get AI prediction, and optionally save to AIResult + MedicalRecord.
    Requires authentication. Saves automatically if the user has a PatientProfile.
    """
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')
        save_to_record = request.data.get('save', True)  # Default: save to DB

        if not image_file:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        ai_prediction = get_ai_prediction(image_file)

        if "error" in ai_prediction:
            error_msg = ai_prediction["error"]
            if getattr(settings, "DEBUG", False):
                return Response(
                    {"error": "AI Model failed to process image", "detail": error_msg},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            return Response({"error": "AI Model failed to process image"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Extract AI output (matches your AI model: predicted_class, confidence, probabilities)
        predicted_class = ai_prediction.get("predicted_class") or ai_prediction.get("prediction") or ai_prediction.get("diagnosis")
        confidence_score = ai_prediction.get("confidence") or ai_prediction.get("confidence_score")
        probabilities = ai_prediction.get("probabilities") or ai_prediction.get("probs")

        if save_to_record:
            try:
                patient_profile = PatientProfile.objects.get(user_id=request.user)
            except PatientProfile.DoesNotExist:
                return Response(
                    {"error": "Create a patient profile first to save results."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ai_result = AIResult.objects.create(
                patient=request.user,
                predicted_class=predicted_class,
                confidence_score=confidence_score,
                probabilities=probabilities,
            )
            medical_record = MedicalRecord.objects.create(
                patient_id=patient_profile,
                ai_result=ai_result,
            )

            return Response({
                "message": "Image analyzed and saved successfully",
                "ai_prediction": ai_prediction,
                "ai_result_id": ai_result.id,
                "medical_record_id": medical_record.id,
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "Image analyzed successfully",
            "ai_prediction": ai_prediction,
        }, status=status.HTTP_200_OK)