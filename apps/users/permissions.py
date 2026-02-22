from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users to view/edit their own profile
    admin can access all profiles
    """
    def has_object_permission(self, request, view, obj):
        # Admin can access everything <3
        if request.user.is_superuser:
            return True
        # Users can only access their own profile <3    
        return obj == request.user


