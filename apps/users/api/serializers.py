from rest_framework import serializers
from apps.users.models import (
    User,
    Staff,
    StaffRole
    )

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Staff
        fields = '__all__'

class StaffRoleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StaffRole
        fields = '__all__'