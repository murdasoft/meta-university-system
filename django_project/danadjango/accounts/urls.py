from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserViewSet, 
    CustomTokenObtainPairView, 
    custom_login, 
    custom_logout, 
    profile,
    password_reset_request,
    password_reset_confirm,
    profile_view,
    upload_avatar,
    quota_view
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # API endpoints (должны быть первыми)
    path('api/', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Password reset
    path('password/reset/', password_reset_request, name='password_reset_request'),
    path('password/reset/confirm/', password_reset_confirm, name='password_reset_confirm'),
    
    # Profile API (должен быть перед веб-страницей)
    path('profile/', profile_view, name='profile_api'),
    path('profile/avatar/', upload_avatar, name='upload_avatar'),
    path('quota/', quota_view, name='quota'),
    
    # Web views (в конце)
    path('login/', custom_login, name='custom_login'),
    path('logout/', custom_logout, name='custom_logout'),
    path('profile-web/', profile, name='profile'),  # Переименован для избежания конфликта
]
