from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .serializers import (
    UserSerializer,
    StaffSerializer,
    StaffRoleSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationRequestSerializer,
    EmailVerificationConfirmSerializer,
    EmailTokenObtainPairSerializer,
    )
from apps.users.models import (
    User,
    Staff,
    StaffRole
    )
from apps.users.permissions import (
    IsOwnerOrAdmin,
    IsStaffOwnerOrAdmin,
    CanManageStaffRoles,
    CanCreateStaff
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model
    Users can view and update their own profile
    Staff and admins can view all users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'first_name', 'last_name', 'date_joined']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Staff can view all users, regular users need authentication
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            # Anyone can create an account (registration)
            permission_classes = []
        else:  # update, partial_update, destroy
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Return all users for staff/admin
        Return only self for regular users
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's profile
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """
        Update current user's profile
        """
        partial = request.method == 'PATCH'
        serializer = self.get_serializer(
            request.user, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def delete_me(self, request):
        """
        Delete current user's account
        """
        request.user.delete()
        return Response(
            {"detail": "Account deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change current user's password
        """
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response(
                {"detail": "Both old_password and new_password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.set_password(new_password)
        request.user.save()
        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK
        )

    
class StaffViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Staff model
    Manages staff members and their clinic assignments
    """
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['user__username', 'user__email', 'hire_date', 'created_at']
    filterset_fields = ['clinic', 'role', 'is_active']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated, CanCreateStaff]
        else:
            permission_classes = [IsAuthenticated, IsStaffOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Return all staff for superusers
        Return staff from same clinic for staff members
        """
        user = self.request.user
        if user.is_superuser:
            return Staff.objects.all()
        
        try:
            staff = user.staff
            # Staff members can see colleagues from their clinic
            return Staff.objects.filter(clinic=staff.clinic)
        except:
            return Staff.objects.none()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's staff profile
        """
        try:
            staff = Staff.objects.get(user=request.user)
            serializer = self.get_serializer(staff)
            return Response(serializer.data)
        except Staff.DoesNotExist:
            return Response(
                {"detail": "No staff profile found for the current user."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Deactivate a staff member
        """
        staff = self.get_object()
        staff.is_active = False
        staff.save()
        return Response(
            {"detail": "Staff member deactivated successfully."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a staff member
        """
        staff = self.get_object()
        staff.is_active = True
        staff.save()
        return Response(
            {"detail": "Staff member activated successfully."},
            status=status.HTTP_200_OK
        )


class StaffRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StaffRole model
    Manages different staff roles/positions
    """
    queryset = StaffRole.objects.all()
    serializer_class = StaffRoleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    permission_classes = [CanManageStaffRoles]

    def get_queryset(self):
        """
        All authenticated staff can view roles
        """
        return StaffRole.objects.all()


class PasswordResetRequestView(APIView):
    """
    Request a password reset email.
    Send a password reset email to the user. Returns success even if email doesn't exist (security).
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security)
            return Response(
                {"message": "If an account with this email exists, a reset link has been sent."},
                status=status.HTTP_200_OK
            )

        # Generate token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build reset URL for frontend
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        reset_url = f"{frontend_url}/reset-password?uid={uid}&token={token}"

        # Send email
        context = {
            'user': user,
            'reset_url': reset_url,
            'expiry_hours': 24
        }
        
        html_message = render_to_string('reset-password.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject="Password Reset - Dentist App",
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_message
        )

        return Response(
            {"message": "If an account with this email exists, a reset link has been sent."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with token.
    Reset the password using the uid and token received via email.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, User.DoesNotExist):
            return Response(
                {"error": "Invalid reset link."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK
        )

class EmailVerificationRequestView(APIView):
    """
    Request an email verification email.
    Send an email verification link to the user.
    """
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationRequestSerializer
    def post(self, request):
        serializer = EmailVerificationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "If an account with this email exists, a verification link has been sent."},
                status=status.HTTP_200_OK
                )
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        verification_url = f"{frontend_url}/verify-email?uid={uid}&token={token}"
        
        context = {
            'user': user,
            'verification_url': verification_url,
            'expiry_hours': 24
        }
        
        html_message = render_to_string('email-verification.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject="Email Verification - Dentist App",
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_message
        )
        return Response(
            {"message": "If an account with this email exists, a verification link has been sent."},
            status=status.HTTP_200_OK
        )

class EmailVerificationConfirmView(APIView):
    """
    Confirm email verification with token.
    Verify the user's email using the uid and token received via email.
    """
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationConfirmSerializer
    
    def post(self, request):
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, User.DoesNotExist):
            return Response(
                {"error": "Invalid verification link."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user.is_email_verified:
            return Response(
                {"message": "Email already verified."},
                status=status.HTTP_200_OK
            )
        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_email_verified = True
        user.save()
        
        return Response(
            {"message": "Email has been verified successfully."},
            status=status.HTTP_200_OK
        )


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Login with email or username and keys tokens in HttpOnly cookies.
    """
    serializer_class = EmailTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')
            
            response.set_cookie(
                'access_token',
                access_token,
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                httponly=True,
                samesite='Lax',
                secure=False, 
            )

            response.set_cookie(
                'refresh_token',
                refresh_token,
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                httponly=True,
                samesite='Lax',
                secure=False, 
            )
            

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Refresh access token using refresh token from cookie.
    """
    def post(self, request, *args, **kwargs):
        if 'refresh' not in request.data and 'refresh_token' in request.COOKIES:
            request.data['refresh'] = request.COOKIES['refresh_token']
        
        try:
            response = super().post(request, *args, **kwargs)
        except (InvalidToken, TokenError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        if response.status_code == 200:
            access_token = response.data.get('access')
            
            response.set_cookie(
                'access_token',
                access_token,
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                httponly=True,
                samesite='Lax',
                secure=False, 
            )

            if 'refresh' in response.data:
                refresh_token = response.data.get('refresh')
                response.set_cookie(
                    'refresh_token',
                    refresh_token,
                    max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                    httponly=True,
                    samesite='Lax',
                    secure=False, 
                )

        return response


class LogoutView(APIView):
    """
    Logout by clearing cookies.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class EmailTokenObtainPairView(TokenObtainPairView):
    """
    Login with email or username.
    Takes email (or username) and password, returns JWT access and refresh tokens.
    DEPRECATED: Use CookieTokenObtainPairView instead.
    """
    serializer_class = EmailTokenObtainPairSerializer