import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Organization

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

class OrganizationJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None  

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None  

        if payload.get("type") != "access":
            return None

        try:
            org = Organization.objects.get(id=payload.get("org_id"))
        except Organization.DoesNotExist:
            return None

        return (org, None)
