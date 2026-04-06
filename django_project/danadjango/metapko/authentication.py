from django.conf import settings
from django.utils import timezone
from rest_framework import authentication
from rest_framework import exceptions

from .models import IntegrationClient


class IntegrationApiKeyAuthentication(authentication.BaseAuthentication):
    """
    Аутентификация по заголовку из settings.METAPKO_API_KEY_HEADER.
    Совпадение по хранимому SHA-256 ключу IntegrationClient.
    """

    keyword = 'Api-Key'

    def authenticate(self, request):
        if not getattr(settings, 'METAPKO_ENABLED', True):
            return None

        header_name = getattr(settings, 'METAPKO_API_KEY_HEADER', 'X-Meta-PKO-Key')
        raw = request.headers.get(header_name)
        if not raw:
            return None

        client = IntegrationClient.verify_key(raw.strip())
        if not client:
            raise exceptions.AuthenticationFailed('Неверный или неактивный API-ключ')

        client.last_used_at = timezone.now()
        client.save(update_fields=['last_used_at'])
        return (client, None)
