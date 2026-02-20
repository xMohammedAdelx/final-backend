from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.patient.api.views import (
    PatientProfileViewSet,
    MedicalRecordViewSet,
    PatientDoctorRelationshipViewSet,
    AIResultViewSet,
    AnalyzeDentalImageView
    )

router = DefaultRouter()
router.register('profiles', PatientProfileViewSet)
router.register('medical-records', MedicalRecordViewSet)
router.register('patient-doctor-relationships', PatientDoctorRelationshipViewSet)
router.register('ai-results', AIResultViewSet, basename='ai-results')

urlpatterns = [
    path('', include(router.urls)),
    path('analyze-dental-image/', AnalyzeDentalImageView.as_view(), name='analyze-dental-image'),
]
