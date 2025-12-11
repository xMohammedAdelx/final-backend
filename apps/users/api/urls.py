from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    StaffViewSet,
    StaffRoleViewSet,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    EmailVerificationRequestView,
    EmailVerificationConfirmView,
    )

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('staff', StaffViewSet)
router.register('staff-roles', StaffRoleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('verify-email/', EmailVerificationRequestView.as_view(), name='email_verification_request'),
    path('verify-email/confirm/', EmailVerificationConfirmView.as_view(), name='email_verification_confirm'),
]
