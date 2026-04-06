"""
Настройки приложения metapko.

Подключаются из danadjango/settings.py отдельным блоком.
Переменные окружения с префиксом METAPKO_* не пересекаются с остальным проектом.
"""

from decouple import config

METAPKO_ENABLED = config('METAPKO_ENABLED', default=True, cast=bool)
METAPKO_API_KEY_HEADER = config('METAPKO_API_KEY_HEADER', default='X-Meta-PKO-Key')

# Подсказка на странице входа /metapko/login/ (для прода задайте свои или отключите пустыми строками)
METAPKO_PORTAL_HINT_LOGIN = config('METAPKO_PORTAL_HINT_LOGIN', default='admin')
METAPKO_PORTAL_HINT_PASSWORD = config('METAPKO_PORTAL_HINT_PASSWORD', default='admin123')
