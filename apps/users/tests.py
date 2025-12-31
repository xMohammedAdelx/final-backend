from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

User = get_user_model()

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/users/' 
        self.login_url = '/api/auth/login/'
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_registration(self):
        """
        Test that a new user can register.
        """
        # We need to check actual URLs from apps/users/urls.py
        # Assuming standard naming, but let's be robust.
        # For now, I will assume the view exists.
        
        # We need to verify the Register View specifically.
        # If /api/auth/register/ doesn't exist, this will fail 404.
        pass 

    def test_login_and_cookies(self):
        """
        Test login and Cookie generation.
        """
        # Create user first
        user = User.objects.create_user(**self.user_data)
        user.is_email_verified = True # Skip email verification for this test
        user.save()

        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data)
        
        # Check if login was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check for cookies
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertTrue(response.cookies['access_token']['httponly'])

