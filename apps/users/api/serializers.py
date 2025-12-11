from rest_framework import serializers
from apps.users.models import (
    User,
    Staff,
    StaffRole
    )

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 
                'profile_picture', 'password', 'is_staff', 'is_active', 'is_email_verified', 'date_joined']
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        """
        Create a new user with properly hashed password
        """
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        
        if password:
            user.set_password(password)  # This hashes the password
        else:
            # Generate a random password if none provided
            user.set_unusable_password()
        
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """
        Update user and properly hash password if provided
        """
        password = validated_data.pop('password', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Only update password if provided
        if password:
            instance.set_password(password)  # This hashes the password
        
        instance.save()
        return instance

class StaffSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Staff
        fields = '__all__'

class StaffRoleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StaffRole
        fields = '__all__'


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset email.
    Send a password reset email to the user.
    """
    email = serializers.EmailField(help_text="User's email address")


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming a password reset.
    Reset the password using the uid and token received via email.
    """
    uid = serializers.CharField(help_text="User ID from reset link (base64 encoded)")
    token = serializers.CharField(help_text="Reset token from reset link")
    new_password = serializers.CharField(
        help_text="New password to set",
        style={'input_type': 'password'},
        write_only=True
    )

class EmailVerificationRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting email verification.
    Send an email verification link to the user.
    """
    email = serializers.EmailField(help_text="User's email address to verify")
    
class EmailVerificationConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming email verification.
    Verify the user's email using the uid and token received via email.
    """
    uid = serializers.CharField(help_text="User ID from verification link (base64 encoded)")
    token = serializers.CharField(help_text="Verification token from email link")