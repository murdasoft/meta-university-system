from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardViewSet, 
    dashboard_index,
    ocr_requests_view,
    languages_view,
    users_view,
    settings_view,
    statistics_view
)

router = DefaultRouter()
router.register(r'api', DashboardViewSet, basename='dashboard')

urlpatterns = [
    # Web views
    path('', dashboard_index, name='dashboard_index'),
    path('ocr-requests/', ocr_requests_view, name='ocr_requests'),
    path('languages/', languages_view, name='languages'),
    path('users/', users_view, name='users'),
    path('settings/', settings_view, name='settings'),
    path('statistics/', statistics_view, name='statistics'),
    
    # API endpoints
    path('', include(router.urls)),
]
