from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.cache import cache
from django.db.models import Count
from ocr.models import RecognitionHistory
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

User = get_user_model()


# Web Views
def custom_login(request):
    """Кастомная страница входа"""
    
    if request.user.is_authenticated:
        return redirect('dashboard_index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Vercel Read-Only Database Fix:
            # Django's login() automatically triggers update_last_login which calls user.save().
            # We mock user.save temporarily to prevent any write attempts to the read-only SQLite DB.
            original_save = user.save
            user.save = lambda *args, **kwargs: None
            
            try:
                login(request, user)
            finally:
                user.save = original_save
                
            messages.success(request, f'Добро пожаловать, {user.username}!')
            next_url = request.POST.get('next') or 'dashboard_index'
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'accounts/login.dj.html')


def custom_logout(request):
    """Выход из системы"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('custom_login')


@login_required(login_url='custom_login')
def profile(request):
    """Профиль пользователя"""
    return render(request, 'accounts/profile.dj.html')


# API Views
class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомный view для получения JWT токенов (авторизация по email)"""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получить информацию о текущем пользователе"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Обновить профиль текущего пользователя"""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Запрос на восстановление пароля"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = User.objects.get(email=email, is_active=True)
        
        # Генерируем токен восстановления (32 символа)
        reset_token = get_random_string(32)
        
        # Сохраняем токен в кеш на 1 час
        cache_key = f'password_reset_{reset_token}'
        cache.set(cache_key, user.id, timeout=3600)  # 1 час
        
        # В реальном приложении здесь должна быть отправка email
        # Для тестирования возвращаем токен в ответе
        return Response({
            'success': True,
            'message': 'Инструкции по восстановлению пароля отправлены на email',
            'reset_token': reset_token,  # Только для разработки! В продакшене убрать
            'expires_in': 3600  # секунды
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Подтверждение восстановления пароля"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    
    if serializer.is_valid():
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        # Проверяем токен в кеше
        cache_key = f'password_reset_{token}'
        user_id = cache.get(cache_key)
        
        if not user_id:
            return Response({
                'success': False,
                'message': 'Неверный или истекший токен восстановления'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Получаем пользователя и меняем пароль
        try:
            user = User.objects.get(id=user_id, is_active=True)
            user.set_password(new_password)
            user.save()
            
            # Удаляем токен из кеша
            cache.delete(cache_key)
            
            return Response({
                'success': True,
                'message': 'Пароль успешно изменен'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Пользователь не найден'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Получить или обновить профиль пользователя
    
    GET /api/accounts/profile/
    PATCH /api/accounts/profile/
    """
    user = request.user
    
    if request.method == 'GET':
        # Статистика пользователя
        total_recognitions = RecognitionHistory.objects.filter(user=user).count()
        total_images = RecognitionHistory.objects.filter(
            user=user
        ).exclude(original_image='').count()
        
        serializer = UserSerializer(user)
        data = serializer.data
        data['stats'] = {
            'total_recognitions': total_recognitions,
            'total_images': total_images,
        }
        
        return Response(data)
    
    elif request.method == 'PATCH':
        # Обновление профиля
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """
    Загрузить аватар пользователя
    
    POST /api/accounts/profile/avatar/
    Body: multipart/form-data с полем 'avatar'
    """
    if 'avatar' not in request.FILES:
        return Response(
            {'detail': 'Файл аватара не предоставлен', 'error_code': 'AVATAR_REQUIRED'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    avatar_file = request.FILES['avatar']
    
    # Валидация размера (максимум 2MB)
    max_size = 2 * 1024 * 1024
    if avatar_file.size > max_size:
        return Response(
            {
                'detail': f'Размер файла превышает 2MB',
                'error_code': 'FILE_TOO_LARGE'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Валидация типа
    valid_extensions = ['jpg', 'jpeg', 'png']
    ext = avatar_file.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        return Response(
            {
                'detail': f'Недопустимый формат. Разрешены: {", ".join(valid_extensions)}',
                'error_code': 'INVALID_FILE_TYPE'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = request.user
        user.avatar = avatar_file
        user.save()
        
        serializer = UserSerializer(user)
        return Response({
            'avatar_url': serializer.data.get('avatar'),
            'message': 'Аватар успешно загружен'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {
                'detail': f'Ошибка при загрузке аватара: {str(e)}',
                'error_code': 'UPLOAD_ERROR'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quota_view(request):
    """
    Проверка лимитов и квот пользователя
    
    GET /api/accounts/quota/
    
    Returns:
    {
        "daily_limit": 100,
        "daily_used": 45,
        "remaining": 55,
        "reset_at": "2024-01-02T00:00:00Z"
    }
    """
    user = request.user
    
    # Лимит запросов в день (100 для бесплатных пользователей)
    daily_limit = 100
    
    # Подсчет использованных запросов за сегодня
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_requests = RecognitionHistory.objects.filter(
        user=user,
        created_at__gte=today_start
    ).count()
    
    # Время сброса (начало следующего дня)
    tomorrow_start = today_start + timedelta(days=1)
    
    return Response({
        'daily_limit': daily_limit,
        'daily_used': today_requests,
        'remaining': max(0, daily_limit - today_requests),
        'reset_at': tomorrow_start.isoformat(),
        'is_limit_exceeded': today_requests >= daily_limit
    })
