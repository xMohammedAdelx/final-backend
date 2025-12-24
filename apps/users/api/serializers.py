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
    
    def validate_username(self, value):
        if value and not value.isalpha() and (len(value) > 255 or len(value) < 2 ):
            raise serializers.ValidationError("Name must contain only letters and be between 2 and 255 characters long.")
        return value

    def validate_phone_number(self, value):
        if value and (not value.isdigit() or len(value) != 11):
            raise serializers.ValidationError("Phone number must contain only digits and be 11 characters long.")
        return value

    def validate_password(self, value):
        if value:
            if len(value) < 8:
                raise serializers.ValidationError("Password must be at least 8 characters long.")
            if not any(char.isdigit() for char in value):
                raise serializers.ValidationError("Password must contain at least one digit.")
            if not any(char.isalpha() for char in value):
                raise serializers.ValidationError("Password must contain at least one letter.")
        return value
    
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
    
    def validate_hire_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Hire date cannot be in the future.")
        return value

class StaffRoleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StaffRole
        fields = '__all__'
    
    def validate_name(self, value):
        if value and not value.isalpha() and (len(value) > 255 or len(value) < 2 ):
            raise serializers.ValidationError("Name must contain only letters and be between 2 and 255 characters long.")
        return value


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