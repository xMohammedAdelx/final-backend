from rest_framework import viewsets, permissions, generics, filters, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from apps.clinic.models import (
    ClinicProfile,
    ClinicService,
    ClinicDoctors,
    ClinicGallery,
    ClinicReview,
    ClinicAppointment,
    ClinicWorkingHours,
    ClinicContactMessage
)
from apps.clinic.api.serializers import (
    ClinicProfileSerializer,
    ClinicServiceSerializer,
    ClinicDoctorsSerializer,
    ClinicGallerySerializer,
    ClinicReviewSerializer,
    ClinicAppointmentSerializer,
    ClinicWorkingHoursSerializer,
    ClinicContactMessageSerializer
)
from apps.clinic.permissions import (
    IsClinicOwnerOrStaff,
    IsClinicStaffOrReadOnly,
    CanManageClinicServices,
    CanManageClinicDoctors,
    IsReviewOwnerOrReadOnly,
    CanAccessAppointment,
    CanManageWorkingHours,
    CanManageContactMessages,
    CanManageGallery,
    CanCreateClinic
)

class ClinicProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Clinic Profiles
    Authenticated users can view all clinics
    Only staff members or admins can create clinic profiles
    Only clinic staff can update/delete their clinic profile
    """
    queryset = ClinicProfile.objects.all()
    serializer_class = ClinicProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address', 'email', 'description']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated, CanCreateClinic]
        else:
            permission_classes = [IsAuthenticated, IsClinicOwnerOrStaff]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def services(self, request, pk=None):
        """
        Get all services offered by this clinic
        """
        clinic = self.get_object()
        services = ClinicService.objects.filter(clinic=clinic)
        serializer = ClinicServiceSerializer(services, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def doctors(self, request, pk=None):
        """
        Get all doctors at this clinic
        """
        clinic = self.get_object()
        doctors = ClinicDoctors.objects.filter(clinic=clinic)
        serializer = ClinicDoctorsSerializer(doctors, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """
        Get all reviews for this clinic
        """
        clinic = self.get_object()
        reviews = ClinicReview.objects.filter(clinic=clinic)
        serializer = ClinicReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def gallery(self, request, pk=None):
        """
        Get all gallery images for this clinic
        """
        clinic = self.get_object()
        gallery = ClinicGallery.objects.filter(clinic=clinic)
        serializer = ClinicGallerySerializer(gallery, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def working_hours(self, request, pk=None):
        """
        Get working hours for this clinic
        """
        clinic = self.get_object()
        hours = ClinicWorkingHours.objects.filter(clinic=clinic)
        serializer = ClinicWorkingHoursSerializer(hours, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        print(f"Creating a new clinic profile with the name: {request.data.get('name')}")
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        print(f"Updating a clinic profile with the name: {request.data.get('name')}")
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(f"Deleting a clinic profile with the name: {instance.name}")
        return super().destroy(request, *args, **kwargs)

class ClinicServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Clinic Services
    Public can view services
    Only clinic staff can manage services
    """
    queryset = ClinicService.objects.all()
    serializer_class = ClinicServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clinic']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, CanManageClinicServices]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Automatically set clinic based on staff membership
        """
        if not self.request.user.is_authenticated:
            raise ValidationError({"detail": "You must be authenticated to create services."})
        else:
            
            try:
                staff = self.request.user.staff
                if staff.is_active:
                    serializer.save(clinic=staff.clinic)
                else:
                    raise ValidationError({"detail": "Your staff account is not active."})
            except:
                # If clinic is provided in request, use it (for admins)
                if self.request.user.is_superuser:
                    serializer.save()
                else:
                    raise ValidationError({"detail": "You must be a staff member to create services."})

class ClinicReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Clinic Reviews
    Public can view reviews
    Authenticated users can create reviews
    Only review owner can update/delete their review
    """
    queryset = ClinicReview.objects.all()
    serializer_class = ClinicReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['comment']
    ordering_fields = ['rating', 'created_at']
    filterset_fields = ['clinic', 'patient', 'rating']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsReviewOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Create review and set patient to current user
        """
        # Check if user already reviewed this clinic
        clinic_id = serializer.validated_data.get('clinic')
        if ClinicReview.objects.filter(patient=self.request.user, clinic=clinic_id).exists():
            raise ValidationError({"detail": "You have already reviewed this clinic."})
        
        serializer.save(patient=self.request.user)

class ClinicAppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Clinic Appointments
    Patients can create and view their appointments
    Clinic staff can view and manage appointments at their clinic
    """
    queryset = ClinicAppointment.objects.all()
    serializer_class = ClinicAppointmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clinic', 'doctor_name', 'date', 'status']
    search_fields = ['patient_name', 'patient_phone']
    ordering_fields = ['date', 'time', 'created_at']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]  # Require authentication to book an appointment
        else:
            permission_classes = [IsAuthenticated, CanAccessAppointment]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Staff can see all appointments at their clinic
        Admins can see all appointments
        Authenticated Patients see THEIR OWN appointments
        """
        user = self.request.user
        
        if user.is_superuser:
            return ClinicAppointment.objects.all()
        
        try:
            staff = user.staff
            if staff.is_active:
                return ClinicAppointment.objects.filter(clinic=staff.clinic)
        except:
            pass
            
        if user.is_authenticated:
            return ClinicAppointment.objects.filter(patient=user)
        
        return ClinicAppointment.objects.none()

    def perform_create(self, serializer):
        """
        Automatically set patient to current user if authenticated
        """
        if self.request.user.is_authenticated:
            serializer.save(patient=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm an appointment (staff only)
        """
        appointment = self.get_object()
        appointment.status = 'confirmed'
        appointment.save()
        return Response(
            {"detail": "Appointment confirmed successfully."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an appointment
        """
        appointment = self.get_object()
        appointment.status = 'cancelled'
        appointment.save()
        return Response(
            {"detail": "Appointment cancelled successfully."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark an appointment as completed (staff only)
        """
        appointment = self.get_object()
        appointment.status = 'completed'
        appointment.save()
        return Response(
            {"detail": "Appointment marked as completed."},
            status=status.HTTP_200_OK
        )

class ClinicWorkingHoursViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Clinic Working Hours
    Public can view working hours
    Only clinic staff can manage working hours
    """
    queryset = ClinicWorkingHours.objects.all()
    serializer_class = ClinicWorkingHoursSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clinic', 'name']
    ordering_fields = ['start_time', 'end_time', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, CanManageWorkingHours]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        try:
            staff = self.request.user.staff
            if staff.is_active:
                serializer.save(clinic=staff.clinic)
            else:
                raise ValidationError({"detail": "Your staff account is not active."})
        except:
            if self.request.user.is_superuser:
                serializer.save()
            else:
                raise ValidationError({"detail": "You must be a staff member to set working hours."})

class ClinicContactMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Clinic Contact Messages
    Anyone can send a message
    Only clinic staff can view/manage messages
    """
    queryset = ClinicContactMessage.objects.all()
    serializer_class = ClinicContactMessageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clinic']
    search_fields = ['name']
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, CanManageContactMessages]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Staff can only see messages for their clinic
        Admins can see all messages
        """
        user = self.request.user
        
        if user.is_superuser:
            return ClinicContactMessage.objects.all()
        
        try:
            staff = user.staff
            if staff.is_active:
                return ClinicContactMessage.objects.filter(clinic=staff.clinic)
        except:
            pass
        
        return ClinicContactMessage.objects.none()

class ClinicGalleryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Clinic Gallery
    Public can view gallery images
    Only clinic staff can manage gallery
    """
    queryset = ClinicGallery.objects.all()
    serializer_class = ClinicGallerySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clinic']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, CanManageGallery]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        try:
            staff = self.request.user.staff
            if staff.is_active:
                serializer.save(clinic=staff.clinic)
            else:
                raise ValidationError({"detail": "Your staff account is not active."})
        except:
            if self.request.user.is_superuser:
                serializer.save()
            else:
                raise ValidationError({"detail": "You must be a staff member to add gallery images."})

class ClinicDoctorsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Clinic Doctors
    Public can view doctors
    Only clinic staff can manage doctors
    """
    queryset = ClinicDoctors.objects.all()
    serializer_class = ClinicDoctorsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clinic']
    search_fields = ['doc_name']
    ordering_fields = ['doc_name', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, CanManageClinicDoctors]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Automatically set clinic based on staff membership
        """
        try:
            staff = self.request.user.staff
            if staff.is_active:
                serializer.save(clinic=staff.clinic)
            else:
                raise ValidationError({"detail": "Your staff account is not active."})
        except:
            if self.request.user.is_superuser:
                serializer.save()
            else:
                raise ValidationError({"detail": "You must be a staff member to add doctors."})
    
    def create(self, request, *args, **kwargs):
        print(f"Creating a new doctor with the name: {request.data.get('doc_name')}")
        return super().create(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        print(f"Listing all doctors")
        return super().list(request, *args, **kwargs)
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        print(f"Retrieving doctor: {instance.doc_name}")
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        print(f"Updating doctor with the name: {request.data.get('doc_name')}")
        return super().update(request, *args, **kwargs)
        
    def partial_update(self, request, *args, **kwargs):
        print(f"Partially updating doctor with fields: {request.data.keys()}")
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(f"Deleting doctor: {instance.doc_name}")
        return super().destroy(request, *args, **kwargs)
    