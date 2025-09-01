from django.urls import path,include
from rest_framework.routers import DefaultRouter 
from .views import (
    ClinicProfileViewSet,
    ClinicServiceViewSet,
    ClinicDoctorsViewSet,
    ClinicGallaryViewSet,
    ClinicReviewViewSet,
    ClinicAppointmentViewSet,
    ClinicWorkingHoursViewSet,
    ClinicContactMessageViewSet
)

router = DefaultRouter()
router.register('profiles',ClinicProfileViewSet)
router.register('services',ClinicServiceViewSet)
router.register('doctors',ClinicDoctorsViewSet)
router.register('gallery',ClinicGallaryViewSet)
router.register('reviews',ClinicReviewViewSet)
router.register('appointments',ClinicAppointmentViewSet)
router.register('working-hours',ClinicWorkingHoursViewSet)
router.register('contact-messages',ClinicContactMessageViewSet)

urlpatterns = [
    path('',include(router.urls)),
]
