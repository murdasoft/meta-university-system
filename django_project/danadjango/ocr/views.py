import base64
import logging
from datetime import datetime, timedelta
from django.db.models import Count, Q, Avg
from django.core.paginator import Paginator
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Language, OCRRequest, OCRSettings, RecognitionHistory
from .serializers import (
    LanguageSerializer,
    OCRRequestSerializer,
    OCRRequestCreateSerializer,
    OCRSettingsSerializer,
    RecognitionHistorySerializer,
    RecognitionHistoryCreateSerializer,
    OCRRecognizeSerializer,
)
from .services import OCRService

logger = logging.getLogger(__name__)


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для языков (только чтение)"""
    
    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer
    permission_classes = [AllowAny]  # Доступен без авторизации
    
    def list(self, request, *args, **kwargs):
        """Список языков в формате для Flutter"""
        languages = self.get_queryset()
        return Response({
            'languages': [
                {
                    'code': lang.code,
                    'name': lang.name,
                    'name_en': lang.name_en or lang.name,
                }
                for lang in languages
            ]
        })


class OCRRequestViewSet(viewsets.ModelViewSet):
    """ViewSet для OCR запросов"""
    
    queryset = OCRRequest.objects.all()
    serializer_class = OCRRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'language']
    search_fields = ['recognized_text']
    ordering_fields = ['created_at', 'confidence']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Пользователи видят только свои запросы, админы - все"""
        if self.request.user.role == 'admin':
            return OCRRequest.objects.all()
        return OCRRequest.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OCRRequestCreateSerializer
        return OCRRequestSerializer
    
    def perform_create(self, serializer):
        """Создать OCR запрос и обработать его"""
        ocr_request = serializer.save(user=self.request.user, status='processing')
        
        try:
            # Получить язык
            language_code = ocr_request.language.code if ocr_request.language else 'ru'
            
            # Обработать изображение
            result = OCRService.process_image(
                ocr_request.image.path,
                language_code
            )
            
            # Обновить запрос
            if result['success']:
                ocr_request.recognized_text = result['text']
                ocr_request.confidence = result['confidence']
                ocr_request.processing_time = result['processing_time']
                ocr_request.status = 'completed'
            else:
                ocr_request.error_message = result['error']
                ocr_request.status = 'failed'
                ocr_request.processing_time = result['processing_time']
            
            ocr_request.save()
            
        except Exception as e:
            logger.error(f"Ошибка при обработке OCR запроса {ocr_request.id}: {str(e)}")
            ocr_request.status = 'failed'
            ocr_request.error_message = str(e)
            ocr_request.save()
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Повторно обработать изображение"""
        ocr_request = self.get_object()
        
        # Проверка прав
        if request.user.role != 'admin' and ocr_request.user != request.user:
            return Response(
                {'detail': 'У вас нет прав для выполнения этого действия'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            ocr_request.status = 'processing'
            ocr_request.save()
            
            language_code = ocr_request.language.code if ocr_request.language else 'ru'
            result = OCRService.process_image(
                ocr_request.image.path,
                language_code
            )
            
            if result['success']:
                ocr_request.recognized_text = result['text']
                ocr_request.confidence = result['confidence']
                ocr_request.processing_time = result['processing_time']
                ocr_request.status = 'completed'
            else:
                ocr_request.error_message = result['error']
                ocr_request.status = 'failed'
                ocr_request.processing_time = result['processing_time']
            
            ocr_request.save()
            
            serializer = self.get_serializer(ocr_request)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Ошибка при повторной обработке OCR запроса {ocr_request.id}: {str(e)}")
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OCRSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet для настроек OCR (только для админов)"""
    
    queryset = OCRSettings.objects.all()
    serializer_class = OCRSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Только админы могут видеть настройки"""
        if self.request.user.role == 'admin':
            return OCRSettings.objects.all()
        return OCRSettings.objects.none()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recognize_text(request):
    """
    Распознавание текста с изображения
    
    POST /api/ocr/recognize/
    Body: {
        "image": "base64_string" или multipart/form-data файл,
        "language": "ru" (опционально)
    }
    """
    # Проверка лимита запросов
    from datetime import datetime
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_requests = RecognitionHistory.objects.filter(
        user=request.user,
        created_at__gte=today_start
    ).count()
    
    if today_requests >= 100:  # Лимит 100 запросов в день
        return Response({
            'detail': 'Дневной лимит запросов исчерпан (100 запросов/день)',
            'error_code': 'QUOTA_EXCEEDED'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Обработка multipart файла
    if 'image' in request.FILES:
        image_file = request.FILES['image']
        image_bytes = image_file.read()
        language_code = request.data.get('language', 'ru')
        # Конвертируем в base64 для Google Vision API
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        image_content = image_base64
    elif 'image' in request.data:
        # Обработка base64 строки
        image_data = request.data.get('image')
        language_code = request.data.get('language', 'ru')
        
        if not image_data:
            return Response({
                'detail': 'Поле image обязательно',
                'error_code': 'IMAGE_REQUIRED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем, что это валидный base64
        try:
            # Пробуем декодировать для проверки
            base64.b64decode(image_data)
            image_content = image_data  # Используем как есть для Google Vision API
        except Exception as e:
            return Response({
                'detail': f'Неверный формат base64: {str(e)}',
                'error_code': 'INVALID_BASE64'
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'detail': 'Изображение не предоставлено. Используйте multipart/form-data с полем "image" или JSON с полем "image" (base64)',
            'error_code': 'IMAGE_REQUIRED'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Распознавание текста (используем image_content - base64 для Google Vision или bytes для Tesseract)
        result = OCRService.recognize_text(image_content, language_code, use_google_vision=True)
        
        if result['success']:
            return Response({
                'text': result['text'],
                'confidence': result['confidence'],
                'language': result.get('language', language_code),
                'processing_time': result['processing_time']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': result.get('error', 'Ошибка распознавания'),
                'error_code': 'RECOGNITION_FAILED'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Ошибка при распознавании: {str(e)}")
        return Response({
            'detail': str(e),
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecognitionHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet для истории распознавания"""
    
    serializer_class = RecognitionHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['language', 'is_favorite']
    search_fields = ['recognized_text']
    ordering_fields = ['created_at', 'confidence']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Пользователи видят только свою историю"""
        queryset = RecognitionHistory.objects.filter(user=self.request.user)
        
        # Фильтры по дате
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to_obj)
            except ValueError:
                pass
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RecognitionHistoryCreateSerializer
        return RecognitionHistorySerializer
    
    def perform_create(self, serializer):
        """Создать запись истории"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Поиск по тексту в истории"""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {'detail': 'Параметр q обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            recognized_text__icontains=query
        )
        
        # Пагинация
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        paginator = Paginator(queryset, page_size)
        
        page_obj = paginator.get_page(page)
        serializer = self.get_serializer(page_obj, many=True)
        
        return Response({
            'count': paginator.count,
            'results': serializer.data,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика по истории пользователя"""
        queryset = self.get_queryset()
        
        total_requests = queryset.count()
        
        # Статистика по языкам
        language_stats = queryset.values('language').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Средняя точность
        avg_confidence_result = queryset.aggregate(
            avg=Avg('confidence')
        )
        avg_confidence = avg_confidence_result.get('avg') or 0.0
        
        # Запросы за последние 30 дней
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_count = queryset.filter(created_at__gte=thirty_days_ago).count()
        
        return Response({
            'total_requests': total_requests,
            'recent_requests': recent_count,
            'language_stats': list(language_stats),
            'avg_confidence': round(avg_confidence, 2),
        })
    
    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        """Добавить/удалить из избранного"""
        history_item = self.get_object()
        
        if request.method == 'POST':
            history_item.is_favorite = True
            history_item.save()
            return Response({'detail': 'Добавлено в избранное'})
        else:
            history_item.is_favorite = False
            history_item.save()
            return Response({'detail': 'Удалено из избранного'})
    
    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """Список избранных записей"""
        queryset = self.get_queryset().filter(is_favorite=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
