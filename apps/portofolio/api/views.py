from rest_framework import viewsets, status, filters, serializers
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    DentistProfileSerializer,
    TestimonialSerializer,
    #ServiceSerializer,
    AppointmentSerializer,
    GallerySerializer
)
from apps.portofolio.models import *
from django_filters.rest_framework import DjangoFilterBackend
from apps.portofolio.permissions import *


class DentistProfileViewSet(viewsets.ModelViewSet):
    queryset = DentistProfile.objects.all()
    serializer_class = DentistProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user_id__first_name', 'user_id__last_name', 'specialty','clinic_name','clinic_address','phone_number','website']
    ordering_fields = ['user_id__first_name', 'user_id__last_name', 'specialty','clinic_name','clinic_address','phone_number','website','created_at']

    def get_permissions(self):
        #Different permissions for different actions:
        #List and retrieve are Anyone or authenticated (for viewing dentist portfolios)
        #Create requires authentication and ownership
        #Update/delete require authentication and ownership
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticatedOrReadOnly]
        elif self.action == "create":
            permission_classes = [IsAuthenticated, IsDentistOwner]
        else:  # update, partial_update, destroy
            permission_classes = [IsAuthenticated, IsDentistOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        #Return all dentist profiles for browsing.
        #Staff can see all, authenticated users can see all for browsing dentists.
        return DentistProfile.objects.all()

    def perform_create(self, serializer):
        #Automatically set the user_id to the requesting user when creating a profile.
        #Prevents creating duplicate profiles for the same user.
        # Check if user already has a dentist profile
        # Staff/Admin can create profiles for other users by providing user_id
        # Dentists can create their own profile
        # Patients cannot create dentist profiles for themselves
        if self.request.user.is_staff or self.request.user.is_superuser:
            # Admin must provide user_id to create profile for specific user
            if 'user_id' not in serializer.validated_data:
                raise serializers.ValidationError(
                    {"detail": "Admin must provide user_id when creating a dentist profile."}
                )
            # Check if that user already has a profile
            target_user = serializer.validated_data['user_id']
            if DentistProfile.objects.filter(user_id=target_user).exists():
                raise serializers.ValidationError(
                    {"detail": f"User {target_user.username} already has a dentist profile."}
                )
            serializer.save()
        else:
            # Non-admin users can only create their own profile
            # Check if user already has a dentist profile
            if DentistProfile.objects.filter(user_id=self.request.user).exists():
                raise serializers.ValidationError(
                    {"detail": "You already have a dentist profile. Use the update endpoint to modify it."}
                )
            # Auto-set user_id to current user
            serializer.save(user_id=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        try:
            profile = DentistProfile.objects.get(user_id=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except DentistProfile.DoesNotExist:
            return Response(
                {"detail": "No dentist profile found for the current user."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["put", "patch"], permission_classes=[IsAuthenticated, IsDentistOwner])
    def update_me(self, request):
        try:
            profile = DentistProfile.objects.get(user_id=request.user)
            partial = request.method == "PATCH"
            serializer = self.get_serializer(
                profile, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except DentistProfile.DoesNotExist:
            return Response(
                {
                    "detail": "No dentist profile found. Please create one first using POST /dentist-profiles/"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated, IsDentistOwner])
    def delete_me(self, request):
        #Delete the dentist profile for the currently authenticated user.
        try:
            profile = DentistProfile.objects.get(user_id=request.user)
            profile.delete()
            return Response(
                {"detail": "Dentist profile deleted successfully."},
                status=status.HTTP_204_NO_CONTENT
            )
        except DentistProfile.DoesNotExist:
            return Response(
                {"detail": "No dentist profile found for the current user."},
                status=status.HTTP_404_NOT_FOUND
            )
    
class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["patient_name", "rating", "feedback"]
    ordering_fields = ["patient_name", "rating", "created_at"]
    filterset_fields = ["dentist_id", "rating"]

    permission_classes = [IsTestimonialOwnerOrAdmin]

    def get_queryset(self):
        #Everyone can see all testimonials (public reviews).
        #Optionally filter by dentist_id to show reviews for specific dentist.
        queryset = Testimonial.objects.all()
        # Filter by dentist if provided in query params
        dentist_id = self.request.query_params.get("dentist_id", None)
        if dentist_id:
            queryset = queryset.filter(dentist_id=dentist_id)
        return queryset

    def perform_create(self, serializer):
        #Create testimonial and verify patient worked with the dentist.
        dentist_id = serializer.validated_data.get("dentist_id")
        # Check if patient has a completed appointment with this dentist
        has_appointment = Appointment.objects.filter(
            patient=self.request.user, dentist_id=dentist_id, status="completed"
        ).exists()
        if not has_appointment:
            raise serializers.ValidationError("You can only review dentists you have completed appointments with.")
        # Auto-set patient and patient_name
        serializer.save(
            patient=self.request.user,
            patient_name=self.request.user.get_full_name()
            or self.request.user.username,
        )
    
    @action(detail=False, methods=["get"])
    def my_testimonials(self, request):
        # Get all testimonials created by the current patient
        testimonials = Testimonial.objects.filter(patient=request.user)
        serializer = self.get_serializer(testimonials, many=True)
        if not testimonials:
            return Response(
                {"detail": "No testimonials found for the current user."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(serializer.data)


# class ServiceViewSet(viewsets.ModelViewSet):
#     queryset = Service.objects.all()
#     serializer_class = ServiceSerializer
#     filter_backends = [
#         DjangoFilterBackend,
#         filters.SearchFilter,
#         filters.OrderingFilter,
#     ]
#     search_fields = ["name", "description", "price", "duration_minutes"]
#     ordering_fields = ["name", "description", "created_at", "price", "duration_minutes"]

#     permission_classes = [IsPublicReadOrDentistAdminWrite, IsDentistOwnerOfRelatedObject]

#     def get_queryset(self):
#         #Public can see all services offered by dentists.
#         queryset = Service.objects.all()
#         # Filtering by dentist_id (e.g., /services/?dentist_id=5)
#         dentist_id = self.request.query_params.get("dentist_id", None)
#         if dentist_id:
#             queryset = queryset.filter(dentist_id=dentist_id)
#         return queryset

#     def perform_create(self, serializer):
#         #Automatically set dentist_id to the authenticated user's dentist profile.
#         # Admin/staff can specify dentist_id in the request data
#         if self.request.user.is_staff or self.request.user.is_superuser:
#             # Admin can create service for any dentist by providing dentist_id
#             if 'dentist_id' not in serializer.validated_data:
#                 raise serializers.ValidationError(
#                     {"detail": "Admin must provide dentist_id when creating service."}
#                 )
#             serializer.save()
#         else:
#             try:
#                 dentist_profile = DentistProfile.objects.get(user_id=self.request.user)
#                 serializer.save(dentist_id=dentist_profile)
#             except DentistProfile.DoesNotExist:
#                 raise serializers.ValidationError(
#                     {"detail": "You must create a dentist profile before adding services."}
#                 )

#     @action(detail=False, methods=["put", "patch"])
#     def update_me(self, request):
#         # Admin/staff can update service for any dentist by providing dentist_id
#         if self.request.user.is_staff or self.request.user.is_superuser:
#             if 'dentist_id' not in request.data:
#                 raise serializers.ValidationError(
#                     {"detail": "Admin must provide dentist_id when updating service."}
#                 )
#             try:
#                 service = Service.objects.get(dentist_id=request.data['dentist_id'])
#                 partial = request.method == "PATCH"
#                 serializer = self.get_serializer(service, data=request.data, partial=partial)
#                 serializer.is_valid(raise_exception=True)
#                 serializer.save()
#                 return Response(serializer.data)
#             except Service.DoesNotExist:
#                 return Response(
#                     {"detail": "No service found for the provided dentist_id."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )
#         else:
#             try:
#                 dentist_profile = DentistProfile.objects.get(user_id=request.user)
#                 service = Service.objects.get(dentist_id=dentist_profile)
#                 partial = request.method == "PATCH"
#                 serializer = self.get_serializer(service, data=request.data, partial=partial)
#                 serializer.is_valid(raise_exception=True)
#                 serializer.save()
#                 return Response(serializer.data)
#             except DentistProfile.DoesNotExist:
#                 return Response(
#                     {"detail": "No dentist profile found for the current user."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )
#             except Service.DoesNotExist:
#                 return Response(
#                     {"detail": "No service found for the current user."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )
    
#     @action(detail=False, methods=["delete"])
#     def delete_me(self, request):
#         if self.request.user.is_staff or self.request.user.is_superuser:
#             if 'dentist_id' not in request.data:
#                 raise serializers.ValidationError(
#                     {"detail": "Admin must provide dentist_id when deleting service."}
#                 )
#             try:
#                 service = Service.objects.get(dentist_id=request.data['dentist_id'])
#                 service.delete()
#                 return Response(
#                     {"detail": "Service deleted successfully."},
#                     status=status.HTTP_204_NO_CONTENT
#                 )
#             except Service.DoesNotExist:
#                 return Response(
#                     {"detail": "No service found for the provided dentist_id."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )
#         else:
#             try:
#                 dentist_profile = DentistProfile.objects.get(user_id=request.user)
#                 service = Service.objects.get(dentist_id=dentist_profile)
#                 service.delete()
#                 return Response(
#                     {"detail": "Service deleted successfully."},
#                     status=status.HTTP_204_NO_CONTENT
#                 )
#             except DentistProfile.DoesNotExist:
#                 return Response(
#                     {"detail": "No dentist profile found for the current user."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )
#             except Service.DoesNotExist:
#                 return Response(
#                     {"detail": "No service found for the current user."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["patient", "doctor_id", "date", "time","status","way_of_communication"]
    ordering_fields = ["patient", "doctor_id", "date", "time", "created_at","status"]

    permission_classes = [IsAuthenticated, CanAccessAppointment]

    def get_queryset(self):
        #Users can only see appointments where they're involved:
        #Patients see their own appointments
        #Dentists see appointments with them
        #Staff see all
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return Appointment.objects.all()
        # Get appointments where user is the patient
        patient_appointments = Appointment.objects.filter(patient=user)
        # Get appointments where user is the dentist
        dentist_profile = DentistProfile.objects.filter(user_id=user).first()
        if dentist_profile:
            dentist_appointments = Appointment.objects.filter(
                dentist_id=dentist_profile
            )
            return (patient_appointments | dentist_appointments).distinct()
        return patient_appointments

    def get_permissions(self):
        #Different permissions for different actions:
        #Patients can create appointments
        #Both patient and dentist can view
        #Only dentist can update appointment status
        if self.action == "create":
            permission_classes = [IsAuthenticated]
        elif self.action in ["update", "partial_update"]:
            # Only dentist or staff can update
            permission_classes = [IsAuthenticated, CanAccessAppointment]
        elif self.action == "destroy":
            # Both patient and dentist can cancel
            permission_classes = [IsAuthenticated, CanAccessAppointment]
        else:
            permission_classes = [IsAuthenticated, CanAccessAppointment]
        return [permission() for permission in permission_classes]


class GalleryViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["description"]
    ordering_fields = ["description", "created_at"]

    permission_classes = [IsPublicReadOrDentistAdminWrite, IsDentistOwnerOfRelatedObject]

    def get_queryset(self):
        #Public can see all gallery images.
        return Gallery.objects.all()

    def perform_create(self, serializer):
        #Automatically set dentist_id to the authenticated user's dentist profile.
        # Admin/staff can specify dentist_id in the request data
        if self.request.user.is_staff or self.request.user.is_superuser:
            # Admin can create gallery for any dentist by providing dentist_id
            if 'dentist_id' not in serializer.validated_data:
                raise serializers.ValidationError(
                    {"detail": "Admin must provide dentist_id when creating gallery."}
                )
            serializer.save()
        else:
            try:
                dentist_profile = DentistProfile.objects.get(user_id=self.request.user)
                serializer.save(dentist_id=dentist_profile)
            except DentistProfile.DoesNotExist:
                raise serializers.ValidationError(
                    {"detail": "You must create a dentist profile before adding Gallery."}
                )

    @action(detail=False, methods=["put", "patch"])
    def update_me(self, request):
        try:
            dentist_profile = DentistProfile.objects.get(user_id=request.user)
            gallery = Gallery.objects.get(dentist_id=dentist_profile)
            partial = request.method == "PATCH"
            serializer = self.get_serializer(gallery, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except DentistProfile.DoesNotExist:
            return Response(
                {"detail": "No dentist profile found for the current user."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Gallery.DoesNotExist:
            return Response(
                {"detail": "No gallery found for the current user."},
                status=status.HTTP_404_NOT_FOUND
            )
    @action(detail=False, methods=["delete"])
    def delete_me(self, request):
        try:
            dentist_profile = DentistProfile.objects.get(user_id=request.user)
            gallery = Gallery.objects.get(dentist_id=dentist_profile)
            gallery.delete()
            return Response(
                {"detail": "Gallery deleted successfully."},
                status=status.HTTP_204_NO_CONTENT
            )
        except DentistProfile.DoesNotExist:
            return Response(
                {"detail": "No dentist profile found for the current user."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Gallery.DoesNotExist:
            return Response(
                {"detail": "No gallery found for the current user."},
                status=status.HTTP_404_NOT_FOUND
            )