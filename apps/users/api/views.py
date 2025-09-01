from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .serializers import (
    UserSerializer,
    StaffSerializer,
    StaffRoleSerializer
    )
from apps.users.models import (
    User,
    Staff,
    StaffRole
    )

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username','email','first_name','last_name']
    ordering_fields = ['username','email','first_name','last_name','created_at']
    
class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username','email','first_name','last_name']
    ordering_fields = ['username','email','first_name','last_name','created_at']
    
class StaffRoleViewSet(viewsets.ModelViewSet):
    queryset = StaffRole.objects.all()
    serializer_class = StaffRoleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name','created_at']