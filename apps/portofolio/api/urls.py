from rest_framework import routers
from .views import (
    DentistProfileViewSet,
    ExperienceViewSet,
    TestimonialViewSet,
    SocialMediaViewSet,
    EducationViewSet,
    SkillViewSet,
    ServiceViewSet,
    ArticleViewSet,
    AwardsViewSet,
    AppointmentViewSet,
    ProjectViewSet,
    FAQViewSet,
    GalleryViewSet,
    CertificationViewSet
)
from django.urls import path, include

router = routers.DefaultRouter()
router.register('dentist-profiles', DentistProfileViewSet)
router.register('experiences', ExperienceViewSet)
router.register('testimonials', TestimonialViewSet)
router.register('social-media', SocialMediaViewSet)
router.register('education', EducationViewSet)
router.register('skills', SkillViewSet)
router.register('services', ServiceViewSet)
router.register('articles', ArticleViewSet)
router.register('awards', AwardsViewSet)
router.register('appointments', AppointmentViewSet)
router.register('projects', ProjectViewSet)
router.register('faqs', FAQViewSet)
router.register('gallery', GalleryViewSet)
router.register('certifications', CertificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]