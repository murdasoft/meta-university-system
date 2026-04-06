from rest_framework.permissions import BasePermission

from .models import IntegrationClient


class HasIntegrationClient(BasePermission):
    """Доступ только после успешной IntegrationApiKeyAuthentication."""

    def has_permission(self, request, view):
        return isinstance(getattr(request, 'user', None), IntegrationClient)
