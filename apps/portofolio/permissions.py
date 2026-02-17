from rest_framework import permissions


class IsDentistOwner(permissions.BasePermission):
    """
    Custom permission to only allow dentists to view/edit/create their own profile
    """
    def has_object_permission(self, request, view, obj):
        #obj is a DentistProfile instance
        #Check if the dentist's user_id matches the requesting user
        return obj.user_id == request.user


class IsDentistOwnerOfRelatedObject(permissions.BasePermission):
    """
    Custom permission for objects related to a dentist profile
    Examples: Experience, Education, Skill, Service, etc
    These objects have a 'dentist_id' field pointing to DentistProfile
    """
    def has_object_permission(self, request, view, obj):
        # obj has a dentist_id field pointing to DentistProfile
        user = request.user
        # Admin can access everything
        if user.is_superuser:
            return True
        # Check if the related dentist profile belongs to this user
        if hasattr(obj, "dentist_id") and obj.dentist_id:
            return obj.dentist_id.user_id == user
        return False


class CanAccessAppointment(permissions.BasePermission):
    """
    Custom permission to allow:
    - Patient to view their own appointments
    - Dentist to view appointments with them
    - Admin to view all appointments
    """
    def has_object_permission(self, request, view, obj):
        # obj is an Appointment instance
        user = request.user
        # Admin can access all
        if user.is_superuser:
            return True
        # Check if user is the patient
        if obj.patient == user:
            return True
        # Check if user is the dentist
        if obj.dentist_id and obj.dentist_id.user_id == user:
            return True
        return False


class IsTestimonialOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission for testimonials
    Anyone can read (public)
    Only authenticated users can create
    Only the patient who created the testimonial or admin can edit/delete
    """
    def has_permission(self, request, view):
        # Read permissions allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions require authentication
        return request.user and request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        # Read permissions allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Admin can do anything
        if request.user.is_superuser:
            return True
        # Check if the user is the patient who created this testimonial
        if hasattr(obj, "patient") and obj.patient:
            return obj.patient == request.user
        return False


class IsPublicReadOrDentistAdminWrite(permissions.BasePermission):
    """
    Custom permission to ensure only dentists and admins can write
    Anyone can read (public)
    Only dentists (users with DentistProfile) and admins can create/update/delete
    """
    def has_permission(self, request, view):
        from apps.portofolio.models import DentistProfile
        
        # Read permissions allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions require authentication
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Admin can do anything
        if request.user.is_superuser:
            return True
        
        # Check if user has a dentist profile
        return DentistProfile.objects.filter(user_id=request.user).exists()
    
    def has_object_permission(self, request, view, obj):
        from apps.portofolio.models import DentistProfile
        
        # Read permissions allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admin can do anything
        if request.user.is_superuser:
            return True
        
        # Check if user has a dentist profile and owns this object
        if hasattr(obj, "dentist_id") and obj.dentist_id:
            return obj.dentist_id.user_id == request.user
        
        return False
