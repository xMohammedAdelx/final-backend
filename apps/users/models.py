
# Create your models here.
from datetime import timezone , timedelta
import secrets
from time import timezone
from django.contrib.auth import authenticate
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.permissions import IsAuthenticated

class User(AbstractUser):
    username = models.CharField(max_length=6767, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username


class StaffRole(models.Model):
    name = models.CharField(max_length=67)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
        
        
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(StaffRole, on_delete=models.SET_NULL, null=True)
    clinic = models.ForeignKey('clinic.ClinicProfile', on_delete=models.CASCADE)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username
    

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    def __str__(self):
        return f"Password reset token for {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_hex(32)
        
        

    def is_valid(self):
        """
        Check if the token is still valid (not expired and not used)
        """
        return self.is_used and timezone.now() < (self.created_at + timedelta(minutes=15))


class EmailBackend:
    """
    Custom authentication backend that allows users to login with email.
    Supports both email and username authentication.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with email or username.
        The 'username' parameter can be either an email or a username.
        """
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if username is None or password is None:
            return None

        # Try to find user by email first
        try:
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            # If not found by email, try username
            try:
                user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                # Run the default password hasher once to reduce timing
                # difference between an existing and a nonexistent user
                User().set_password(password)
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def get_user(self, user_id):
        """
        Retrieve user by primary key.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None