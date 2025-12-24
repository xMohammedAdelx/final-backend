from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users to view/edit their own profile
    Staff and admin can access all profiles
    """
    def has_object_permission(self, request, view, obj):
        # Staff/Admin can access everything
        if request.user.is_staff or request.user.is_superuser:
            return True
        # Users can only access their own profile
        return obj == request.user


class IsStaffOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission for Staff objects
    Only the user themselves or admins can manage staff records
    """
    def has_object_permission(self, request, view, obj):
        # Admin/superuser can do anything
        if request.user.is_superuser:
            return True
        # Staff members can view
        if request.method in permissions.SAFE_METHODS and request.user.is_staff:
            return True
        # Users can only manage their own staff record
        return obj.user == request.user


class CanManageStaffRoles(permissions.BasePermission):
    """
    Custom permission for managing staff roles
    Only admins and superusers can create/update/delete roles
    Staff can view roles
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to staff
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_staff
        # Write permissions only for superusers
        return request.user and request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        # Read permissions allowed to staff
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_staff
        # Write permissions only for superusers
        return request.user and request.user.is_superuser


class IsStaffMemberOfClinic(permissions.BasePermission):
    """
    Custom permission to check if user is a staff member of a specific clinic
    """
    def has_permission(self, request, view):
        # Must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin/superuser can do anything
        if request.user.is_superuser or request.user.is_staff:
            return True
        # Check if user is staff of the clinic
        try:
            staff = request.user.staff
            return staff.clinic == obj.clinic if hasattr(obj, 'clinic') else False
        except:
            return False


class CanCreateStaff(permissions.BasePermission):
    """
    Custom permission for creating staff
    Only clinic owners or admins can create staff for their clinic
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            # Only superusers and staff can create staff members
            return request.user and (request.user.is_superuser or request.user.is_staff)
        return request.user and request.user.is_authenticated

