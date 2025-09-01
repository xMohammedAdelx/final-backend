from rest_framework import viewsets, permissions , generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.clinic.models import (
    ClinicProfile,
    ClinicService,
    ClinicDoctors,
    ClinicGallary,
    ClinicReview,
    ClinicAppointment,
    ClinicWorkingHours,
    ClinicContactMessage
)
from apps.clinic.api.serializers import (
    ClinicProfileSerializer,
    ClinicServiceSerializer,
    ClinicDoctorsSerializer,
    ClinicGallarySerializer,
    ClinicReviewSerializer,
    ClinicAppointmentSerializer,
    ClinicWorkingHoursSerializer,
    ClinicContactMessageSerializer
)

class ClinicProfileViewSet(viewsets.ModelViewSet):
    queryset = ClinicProfile.objects.all()
    serializer_class = ClinicProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name','address','email']
    ordering_fields = ['name','created_at']
    
    @action(detail=True, methods=['get'])
    def services(self, request, pk=None):
        clinic = self.get_object()
        services = ClinicService.objects.filter(clinic=clinic)
        serializer = ClinicServiceSerializer(services, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def doctors(self, request, pk=None):
        clinic = self.get_object()
        doctors = ClinicDoctors.objects.filter(clinic=clinic)
        serializer = ClinicDoctorsSerializer(doctors, many=True)
        return Response(serializer.data)

class ClinicServiceViewSet(viewsets.ModelViewSet):
    queryset = ClinicService.objects.all()
    serializer_class = ClinicServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clinic']
    search_fields = ['name','description']
    ordering_fields = ['name','price','created_at']

class ClinicReviewViewSet(viewsets.ModelViewSet):
    queryset = ClinicReview.objects.all()
    serializer_class = ClinicReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['comment']
    ordering_fields = ['rating','created_at']
    filterset_fields = ['clinic','patient']
    def get_permissions(self):
        if self.action in ['list','retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class ClinicAppointmentViewSet(viewsets.ModelViewSet):
    queryset = ClinicAppointment.objects.all()
    serializer_class = ClinicAppointmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clinic','doctor_name','patient_name']
    search_fields = ['patient_name','doctor_name']
    ordering_fields = ['date','time','created_at']

class ClinicWorkingHoursViewSet(viewsets.ModelViewSet):
    queryset = ClinicWorkingHours.objects.all()
    serializer_class = ClinicWorkingHoursSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clinic','name']
    ordering_fields = ['start_time','end_time','created_at']

class ClinicContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ClinicContactMessage.objects.all()
    serializer_class = ClinicContactMessageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clinic']
    search_fields = ['name']
    ordering_fields = ['created_at']

class ClinicGallaryViewSet(viewsets.ModelViewSet):
    queryset = ClinicGallary.objects.all()
    serializer_class = ClinicGallarySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clinic']
    search_fields = ['title','description']
    ordering_fields = ['title','created_at']

class ClinicDoctorsViewSet(viewsets.ModelViewSet):
    queryset = ClinicDoctors.objects.all()
    serializer_class = ClinicDoctorsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clinic']
    search_fields = ['doc_name']
    ordering_fields = ['doc_name','created_at']
