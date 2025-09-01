from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    StaffViewSet,
    StaffRoleViewSet
    )

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('staff', StaffViewSet)
router.register('staff-roles', StaffRoleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
