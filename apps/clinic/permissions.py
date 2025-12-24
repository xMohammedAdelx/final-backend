from rest_framework import permissions


class CanCreateClinic(permissions.BasePermission):
    """
    Custom permission to only allow superusers or existing staff members to create clinics
    Regular users/patients cannot create clinics
    """
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        try:
            staff = request.user.staff
            return staff.is_active
        except:
            return False


class IsClinicOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow clinic owners or their staff to manage clinic data
    """
    def has_object_permission(self, request, view, obj):
        # Admin/superuser can access everything
        if request.user.is_superuser:
            return True
        
        # Get the clinic from the object
        clinic = obj if hasattr(obj, 'name') else getattr(obj, 'clinic', None)
        
        if not clinic:
            return False
        
        # Check if user is staff of this clinic
        try:
            staff = request.user.staff
            return staff.clinic == clinic and staff.is_active
        except:
            return False


class IsClinicStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission for clinic-related objects
    Anyone can read (for browsing clinics)
    Only clinic staff can create/update/delete
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions require authentication
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions allowed to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admin/superuser can do anything
        if request.user.is_superuser:
            return True
        
        # Get the clinic from the object
        clinic = obj if hasattr(obj, 'name') else getattr(obj, 'clinic', None)
        
        if not clinic:
            return False
        
        # Check if user is staff of this clinic
        try:
            staff = request.user.staff
            return staff.clinic == clinic and staff.is_active
        except:
            return False


class CanManageClinicServices(permissions.BasePermission):
    """
    Custom permission for managing clinic services
    Only clinic staff can create/update/delete services
    Everyone can view
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user.is_superuser:
            return True
        
        try:
            staff = request.user.staff
            return staff.clinic == obj.clinic and staff.is_active
        except:
            return False


class CanManageClinicDoctors(permissions.BasePermission):
    """
    Custom permission for managing clinic doctors
    Only clinic staff can create/update/delete doctors
    Everyone can view
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user.is_superuser:
            return True
        
        try:
            staff = request.user.staff
            return staff.clinic == obj.clinic and staff.is_active
        except:
            return False


class IsReviewOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission for clinic reviews
    Anyone can read reviews (public)
    Only authenticated users can create reviews
    Only the review author or admin can update/delete
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
        
        # Only the patient who created the review can edit/delete
        return obj.patient == request.user


class CanAccessAppointment(permissions.BasePermission):
    """
    Custom permission to allow:
    - Patient to view/manage their own appointments
    - Clinic staff to view/manage appointments at their clinic
    - Admin to view/manage all appointments
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin can access all
        if request.user.is_superuser:
            return True
        
        # Check if user is staff of this clinic
        try:
            staff = request.user.staff
            if staff.clinic == obj.clinic and staff.is_active:
                return True
        except:
            pass
        
        # Check if user is the patient
        if obj.patient == request.user:
            return True
            
        return False


class CanManageWorkingHours(permissions.BasePermission):
    """
    Custom permission for managing clinic working hours
    Only clinic staff can create/update/delete working hours
    Everyone can view
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user.is_superuser:
            return True
        
        try:
            staff = request.user.staff
            return staff.clinic == obj.clinic and staff.is_active
        except:
            return False


class CanManageContactMessages(permissions.BasePermission):
    """
    Custom permission for managing contact messages
    Anyone can create contact messages
    Only clinic staff can view/update/delete their clinic's messages
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True  # Anyone can send a message
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        try:
            staff = request.user.staff
            return staff.clinic == obj.clinic and staff.is_active
        except:
            return False


class CanManageGallery(permissions.BasePermission):
    """
    Custom permission for managing clinic gallery
    Everyone can view gallery images
    Only clinic staff can create/update/delete images
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user.is_superuser:
            return True
        
        try:
            staff = request.user.staff
            return staff.clinic == obj.clinic and staff.is_active
        except:
            return False

