from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ocr.models import OCRRequest, Language, OCRSettings
from metapko.models import Teacher, Course, StudyGroup
from scheduler.models import AssignmentResult
import json

User = get_user_model()


@login_required(login_url='custom_login')
def dashboard_index(request):
    """Главная страница дашборда"""
    
    # Общая статистика
    total_requests = OCRRequest.objects.count()
    completed_requests = OCRRequest.objects.filter(status='completed').count()
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Последние запросы
    recent_requests = OCRRequest.objects.select_related('user', 'language').order_by('-created_at')[:10]
    
    # Статистика по дням (последние 7 дней)
    today = datetime.now().date()
    daily_labels = []
    daily_completed = []
    daily_failed = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        daily_labels.append(date.strftime('%d.%m'))
        
        day_requests = OCRRequest.objects.filter(created_at__date=date)
        daily_completed.append(day_requests.filter(status='completed').count())
        daily_failed.append(day_requests.filter(status='failed').count())
    
    # Статистика по языкам
    language_stats = OCRRequest.objects.values('language__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    language_labels = [stat['language__name'] or 'Не указан' for stat in language_stats]
    language_data = [stat['count'] for stat in language_stats]
    
    context = {
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'total_users': total_users,
        'active_users': active_users,
        'total_teachers': Teacher.objects.count(),
        'total_courses': Course.objects.count(),
        'total_groups': StudyGroup.objects.count(),
        'total_assignments': AssignmentResult.objects.count(),
        'recent_requests': recent_requests,
        'daily_labels': json.dumps(daily_labels),
        'daily_completed': json.dumps(daily_completed),
        'daily_failed': json.dumps(daily_failed),
        'language_labels': json.dumps(language_labels),
        'language_data': json.dumps(language_data),
    }
    
    return render(request, 'dashboard/index.dj.html', context)


@login_required(login_url='custom_login')
def ocr_requests_view(request):
    """Страница со списком OCR запросов"""
    
    # Получить все запросы с пагинацией
    requests_list = OCRRequest.objects.select_related('user', 'language').order_by('-created_at')
    
    # Статистика по статусам
    status_stats = OCRRequest.objects.values('status').annotate(count=Count('id'))
    
    context = {
        'requests_list': requests_list[:50],  # Первые 50
        'total_count': requests_list.count(),
        'status_stats': status_stats,
    }
    
    return render(request, 'dashboard/ocr_requests.dj.html', context)


@login_required(login_url='custom_login')
def languages_view(request):
    """Страница управления языками"""
    
    languages = Language.objects.annotate(
        requests_count=Count('ocr_requests')
    ).order_by('code')
    
    context = {
        'languages': languages,
    }
    
    return render(request, 'dashboard/languages.dj.html', context)


@login_required(login_url='custom_login')
def users_view(request):
    """Страница управления пользователями"""
    from ocr.models import RecognitionHistory
    
    users = User.objects.annotate(
        requests_count=Count('ocr_requests', distinct=True),
        recognition_count=Count('recognition_history', distinct=True)
    ).order_by('-date_joined')
    
    # Статистика по ролям
    role_stats = User.objects.values('role').annotate(count=Count('id'))
    
    # Общая статистика
    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    
    context = {
        'users_list': users,
        'role_stats': role_stats,
        'total_users': total_users,
        'active_users': active_users,
    }
    
    return render(request, 'dashboard/users.dj.html', context)


@login_required(login_url='custom_login')
def settings_view(request):
    """Страница настроек API ключей и OCR"""
    from django.shortcuts import redirect
    from django.contrib import messages
    from dashboard.models import APIKey
    
    # Разрешаем доступ всем авторизованным пользователям для просмотра
    # Но только админы могут изменять
    
    api_keys = APIKey.objects.all()
    ocr_settings = OCRSettings.objects.first()
    languages = Language.objects.all()
    
    # Обработка POST запросов (все авторизованные пользователи могут добавлять ключи)
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_key':
            # Создание нового ключа
            name = request.POST.get('name')
            key_type = request.POST.get('key_type')
            api_key = request.POST.get('api_key', '').strip()
            description = request.POST.get('description', '')
            
            if name and api_key:
                APIKey.objects.create(
                    name=name,
                    key_type=key_type,
                    api_key=api_key,
                    description=description,
                    is_active=True
                )
                messages.success(request, f'Ключ "{name}" успешно создан')
            else:
                messages.error(request, 'Название и API ключ обязательны')
        
        elif action == 'update_key':
            # Обновление ключа
            key_id = request.POST.get('key_id')
            try:
                api_key_obj = APIKey.objects.get(id=key_id)
                api_key_obj.name = request.POST.get('name', api_key_obj.name)
                api_key_obj.key_type = request.POST.get('key_type', api_key_obj.key_type)
                api_key_obj.is_active = request.POST.get('is_active') == 'on'
                api_key_obj.description = request.POST.get('description', '')
                
                if request.POST.get('api_key'):
                    api_key_obj.api_key = request.POST.get('api_key').strip()
                
                api_key_obj.save()
                messages.success(request, f'Ключ "{api_key_obj.name}" обновлен')
            except APIKey.DoesNotExist:
                messages.error(request, 'Ключ не найден')
        
        elif action == 'delete_key':
            # Удаление ключа
            key_id = request.POST.get('key_id')
            try:
                api_key_obj = APIKey.objects.get(id=key_id)
                name = api_key_obj.name
                api_key_obj.delete()
                messages.success(request, f'Ключ "{name}" удален')
            except APIKey.DoesNotExist:
                messages.error(request, 'Ключ не найден')
        
        return redirect('settings')
    
    context = {
        'api_keys': api_keys,
        'ocr_settings': ocr_settings,
        'languages': languages,
    }
    
    return render(request, 'dashboard/settings.dj.html', context)


@login_required(login_url='custom_login')
def statistics_view(request):
    """Страница детальной статистики"""
    
    # Общая статистика
    total_requests = OCRRequest.objects.count()
    completed = OCRRequest.objects.filter(status='completed').count()
    failed = OCRRequest.objects.filter(status='failed').count()
    processing = OCRRequest.objects.filter(status='processing').count()
    
    # Средние показатели
    avg_stats = OCRRequest.objects.filter(status='completed').aggregate(
        avg_time=Avg('processing_time'),
        avg_confidence=Avg('confidence')
    )
    
    # Статистика по месяцам (последние 12)
    today = datetime.now().date()
    monthly_labels = []
    monthly_data = []
    
    for i in range(11, -1, -1):
        date = today - timedelta(days=i*30)
        monthly_labels.append(date.strftime('%B'))
        count = OCRRequest.objects.filter(
            created_at__month=date.month,
            created_at__year=date.year
        ).count()
        monthly_data.append(count)
    
    # Академическая статистика
    academy_stats = {
        'total_teachers': Teacher.objects.count(),
        'total_courses': Course.objects.count(),
        'total_groups': StudyGroup.objects.count(),
        'total_assignments': AssignmentResult.objects.count(),
    }

    context = {
        'total_requests': total_requests,
        'completed': completed,
        'failed': failed,
        'processing': processing,
        'avg_time': avg_stats['avg_time'],
        'avg_confidence': avg_stats['avg_confidence'],
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
        'academy': academy_stats,
    }
    
    return render(request, 'dashboard/statistics.dj.html', context)


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet для статистики дашборда"""
    
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Получить общую статистику"""
        
        # Только админы могут просматривать дашборд
        if request.user.role != 'admin':
            return Response(
                {'detail': 'У вас нет прав для просмотра дашборда'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Получить статистику за последние 30 дней
        today = datetime.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Общая статистика
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        total_requests = OCRRequest.objects.count()
        
        # Статистика запросов
        requests_stats = OCRRequest.objects.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            failed=Count('id', filter=Q(status='failed')),
            processing=Count('id', filter=Q(status='processing')),
            avg_time=Avg('processing_time', filter=Q(status='completed')),
            avg_confidence=Avg('confidence', filter=Q(status='completed'))
        )
        
        # Статистика за последние 30 дней
        recent_requests = OCRRequest.objects.filter(
            created_at__date__gte=thirty_days_ago
        ).count()
        
        # Статистика по языкам
        languages_stats = OCRRequest.objects.values(
            'language__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Статистика по дням (последние 7 дней)
        seven_days_ago = today - timedelta(days=7)
        daily_stats = []
        
        for i in range(7):
            date = today - timedelta(days=i)
            day_requests = OCRRequest.objects.filter(
                created_at__date=date
            )
            
            daily_stats.append({
                'date': date.isoformat(),
                'total': day_requests.count(),
                'completed': day_requests.filter(status='completed').count(),
                'failed': day_requests.filter(status='failed').count(),
            })
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'total_requests': total_requests,
            'recent_requests': recent_requests,
            'requests_stats': requests_stats,
            'languages_stats': list(languages_stats),
            'daily_stats': daily_stats,
        })
    
    @action(detail=False, methods=['get'])
    def users_stats(self, request):
        """Статистика пользователей"""
        
        if request.user.role != 'admin':
            return Response(
                {'detail': 'У вас нет прав для просмотра этой статистики'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Топ пользователей по количеству запросов
        top_users = User.objects.annotate(
            requests_count=Count('ocr_requests')
        ).order_by('-requests_count')[:10]
        
        users_data = [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'requests_count': user.requests_count,
            'date_joined': user.date_joined,
        } for user in top_users]
        
        return Response({
            'top_users': users_data
        })
    
    @action(detail=False, methods=['get'])
    def performance(self, request):
        """Статистика производительности"""
        
        if request.user.role != 'admin':
            return Response(
                {'detail': 'У вас нет прав для просмотра этой статистики'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Средняя производительность
        performance_stats = OCRRequest.objects.filter(
            status='completed'
        ).aggregate(
            avg_processing_time=Avg('processing_time'),
            avg_confidence=Avg('confidence')
        )
        
        return Response(performance_stats)
