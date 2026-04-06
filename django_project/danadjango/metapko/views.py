from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import IntegrationApiKeyAuthentication
from .permissions import HasIntegrationClient


class HealthView(APIView):
    """Публичная проверка доступности сервиса (без ключа)."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        enabled = getattr(settings, 'METAPKO_ENABLED', True)
        return Response({
            'status': 'ok',
            'service': 'metapko',
            'enabled': enabled,
        })


class ProtectedInfoView(APIView):
    """Пример защищённого эндпоинта — только с валидным API-ключом."""

    authentication_classes = [IntegrationApiKeyAuthentication]
    permission_classes = [HasIntegrationClient]

    def get(self, request):
        client = request.user
        return Response({
            'message': 'Доступ разрешён',
            'client': client.name,
            'client_id': client.pk,
        })
