"""
URL configuration for danadjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from metapko.admin_site import meta_pko_admin

# Swagger/OpenAPI schema
schema_view = get_schema_view(
    openapi.Info(
        title="Qazaqdana OCR API",
        default_version='v1',
        description="API для распознавания текста с изображений (русский, казахский, английский)",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@qazaqdana.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

metapko_schema_view = get_schema_view(
    openapi.Info(
        title="Meta-PKO Integration API",
        default_version='v1',
        description=(
            "Интеграционное API (внешние сервисы, Telegram-бот). "
            "Аутентификация для защищённых методов: заголовок X-Meta-PKO-Key (или METAPKO_API_KEY_HEADER в .env)."
        ),
    ),
    patterns=[path('api/metapko/', include('metapko.api_urls'))],
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Главная страница - перенаправление на вход
    path('', RedirectView.as_view(url='/login/', permanent=False), name='home'),
    
    # Авторизация
    path('', include('accounts.urls')),
    
    # Dashboard (требует авторизации)
    path('dashboard/', include('dashboard.urls')),
    
    # Django Admin (стандартный) и отдельная админка Meta-PKO (только модели metapko)
    path('admin/', admin.site.urls),
    path('meta-admin/', meta_pko_admin.urls),
    path('metapko/', include('metapko.portal_urls')),
    
    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/ocr/', include('ocr.urls')),
    path('api/storage/', include('storage.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/vacancies-mock/', include('job_portal_mock.urls')),
    path('api/ai/', include('ai_assistant.urls')),
    path('api/metapko/', include('metapko.api_urls')),

    # Scheduler
    path('scheduler/', include('scheduler.urls')),

    # Swagger/OpenAPI documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(
        'meta-swagger/',
        metapko_schema_view.with_ui('swagger', cache_timeout=0),
        name='metapko-schema-swagger-ui',
    ),
]

# Медиа файлы в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
