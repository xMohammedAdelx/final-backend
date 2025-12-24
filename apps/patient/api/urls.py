from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.patient.api.views import (
    PatientProfileViewSet,
    MedicalRecordViewSet,
    PrescriptionViewSet,
    PatientDoctorRelationshipViewSet,
    AITreatmentSuggestionViewSet
    )

router = DefaultRouter()
router.register('profiles', PatientProfileViewSet)
router.register('medical-records', MedicalRecordViewSet)
router.register('prescriptions', PrescriptionViewSet)
router.register('patient-doctor-relationships', PatientDoctorRelationshipViewSet)
router.register('ai-suggestions', AITreatmentSuggestionViewSet, basename='ai-suggestions')

urlpatterns = [
    path('', include(router.urls)),
]
