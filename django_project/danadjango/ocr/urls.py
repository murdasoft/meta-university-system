from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LanguageViewSet,
    OCRRequestViewSet,
    OCRSettingsViewSet,
    RecognitionHistoryViewSet,
    recognize_text
)

router = DefaultRouter()
router.register(r'languages', LanguageViewSet, basename='language')
router.register(r'requests', OCRRequestViewSet, basename='ocr-request')
router.register(r'settings', OCRSettingsViewSet, basename='ocr-settings')
router.register(r'history', RecognitionHistoryViewSet, basename='recognition-history')

urlpatterns = [
    path('', include(router.urls)),
    path('recognize/', recognize_text, name='recognize_text'),
]
