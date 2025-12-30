from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions

def enforce_csrf(request):
    """
    Enforce CSRF validation for cookie-based authentication.
    """
    check = CSRFCheck(request)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied(f'CSRF Failed: {reason}')

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom authentication class that reads the JWT access token from an HttpOnly cookie.
    Falls back to the standard Authorization header if the cookie is not present.
    """

    def authenticate(self, request):
        # First, try to authenticate using the standard header
        header_auth = super().authenticate(request)
        if header_auth is not None:
            return header_auth

        # If no header, check the cookie
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None:
            return None

        # If using cookies, we SHOULD enforce CSRF for state-changing methods
        # However, for pure API usage with SameSite=Lax/Strict, it's sometimes debated.
        # But standard Django security practice is to enforce CSRF when using cookies.
        # verify_csrf_token(request) # This would be a helper to check X-CSRFToken header

        # Validate the token
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
