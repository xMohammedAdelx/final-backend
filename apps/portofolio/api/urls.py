from rest_framework import routers
from .views import (
    DentistProfileViewSet,
    TestimonialViewSet,
    #ServiceViewSet,
    AppointmentViewSet,
    GalleryViewSet
)
from django.urls import path, include

router = routers.DefaultRouter()
router.register('dentist-profiles', DentistProfileViewSet)
router.register('testimonials', TestimonialViewSet)
#router.register('services', ServiceViewSet)
router.register('appointments', AppointmentViewSet)
router.register('gallery', GalleryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]