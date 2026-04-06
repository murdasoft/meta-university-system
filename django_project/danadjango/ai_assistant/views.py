from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ChatSession, ChatMessage, AIUsageQuota
from .serializers import (
    ChatRequestSerializer,
    ChatSessionSerializer,
    ChatMessageSerializer,
    QuickActionSerializer,
    AIUsageQuotaSerializer
)
from .services import AIAssistantService


@swagger_auto_schema(
    method='post',
    operation_description='Отправить сообщение AI ассистенту',
    request_body=ChatRequestSerializer,
    responses={
        200: openapi.Response(
            description='Успешный ответ',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'session_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                    'response': openapi.Schema(type=openapi.TYPE_STRING),
                    'processing_time': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'remaining_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )
        ),
        400: 'Ошибка валидации',
        403: 'Достигнут лимит вопросов',
        500: 'Ошибка сервера'
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_view(request):
    """
    AI чат для работы с распознанным текстом
    
    POST /api/ai/chat/
    {
        "message": "Переведи на русский",
        "session_id": "uuid" (опционально),
        "recognition_text": "распознанный текст" (опционально),
        "language": "ru"
    }
    """
    serializer = ChatRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    message_text = serializer.validated_data['message']
    session_id = serializer.validated_data.get('session_id')
    recognition_text = serializer.validated_data.get('recognition_text')
    language = serializer.validated_data.get('language', 'ru')
    
    # Проверка квоты
    quota, created = AIUsageQuota.objects.get_or_create(user=user)
    can_ask, error_message = quota.can_ask_question()
    
    if not can_ask:
        return Response(
            {
                'error': error_message,
                'remaining_questions': 0,
                'is_premium': False
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Получаем или создаём сессию
    if session_id:
        try:
            session = ChatSession.objects.get(id=session_id, user=user)
        except ChatSession.DoesNotExist:
            session = ChatSession.objects.create(
                user=user,
                recognition_text=recognition_text
            )
    else:
        session = ChatSession.objects.create(
            user=user,
            recognition_text=recognition_text
        )
    
    # Сохраняем сообщение пользователя
    user_message = ChatMessage.objects.create(
        session=session,
        role='user',
        content=message_text
    )
    
    # Получаем историю сообщений для контекста (последние 10)
    previous_messages = session.messages.order_by('created_at')[:10]
    messages_for_ai = [
        {'role': msg.role, 'content': msg.content}
        for msg in previous_messages
    ]
    
    # Отправляем в AI
    ai_result = AIAssistantService.chat(
        messages=messages_for_ai,
        recognition_text=recognition_text or session.recognition_text,
        language=language
    )
    
    if not ai_result['success']:
        return Response(
            {'error': ai_result['error']},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Сохраняем ответ AI
    assistant_message = ChatMessage.objects.create(
        session=session,
        role='assistant',
        content=ai_result['response']
    )
    
    # Увеличиваем счётчик использования
    quota.increment_usage()
    
    # Обновляем квоту
    quota.refresh_from_db()
    
    return Response({
        'session_id': str(session.id),
        'response': ai_result['response'],
        'processing_time': ai_result['processing_time'],
        'remaining_questions': max(0, 5 - quota.daily_questions_used) if quota.user.role != 'premium' else -1,
    })


@swagger_auto_schema(
    method='post',
    operation_description='Быстрые действия с текстом (перевод, исправление, резюме)',
    request_body=QuickActionSerializer,
    responses={
        200: openapi.Response(
            description='Успешный ответ',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'result': openapi.Schema(type=openapi.TYPE_STRING),
                    'processing_time': openapi.Schema(type=openapi.TYPE_NUMBER),
                }
            )
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_action_view(request):
    """
    Быстрые действия с текстом
    
    POST /api/ai/quick-action/
    {
        "action": "translate_ru",
        "text": "Hello world",
        "language": "ru"
    }
    """
    serializer = QuickActionSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    # Проверка квоты
    quota, created = AIUsageQuota.objects.get_or_create(user=user)
    can_ask, error_message = quota.can_ask_question()
    
    if not can_ask:
        return Response(
            {'error': error_message},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Выполняем действие
    result = AIAssistantService.quick_action(
        action=serializer.validated_data['action'],
        text=serializer.validated_data['text'],
        language=serializer.validated_data.get('language', 'ru')
    )
    
    if not result['success']:
        return Response(
            {'error': result['error']},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Увеличиваем счётчик
    quota.increment_usage()
    
    return Response({
        'result': result['response'],
        'processing_time': result['processing_time'],
    })


@swagger_auto_schema(
    method='get',
    operation_description='Получить историю чата',
    responses={200: ChatSessionSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history_view(request):
    """
    Получить историю чатов пользователя
    
    GET /api/ai/history/
    """
    sessions = ChatSession.objects.filter(user=request.user).prefetch_related('messages')
    serializer = ChatSessionSerializer(sessions, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_description='Получить сессию чата по ID',
    responses={200: ChatSessionSerializer()}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_session_view(request, session_id):
    """
    Получить конкретную сессию чата
    
    GET /api/ai/session/{session_id}/
    """
    try:
        session = ChatSession.objects.prefetch_related('messages').get(
            id=session_id,
            user=request.user
        )
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Сессия не найдена'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ChatSessionSerializer(session)
    return Response(serializer.data)


@swagger_auto_schema(
    method='delete',
    operation_description='Удалить сессию чата',
    responses={204: 'Успешно удалено'}
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_chat_session_view(request, session_id):
    """
    Удалить сессию чата
    
    DELETE /api/ai/session/{session_id}/
    """
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Сессия не найдена'},
            status=status.HTTP_404_NOT_FOUND
        )


@swagger_auto_schema(
    method='get',
    operation_description='Получить квоту использования AI',
    responses={200: AIUsageQuotaSerializer()}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_quota_view(request):
    """
    Получить информацию о квоте использования AI
    
    GET /api/ai/quota/
    """
    quota, created = AIUsageQuota.objects.get_or_create(user=request.user)
    quota.reset_if_needed()
    
    serializer = AIUsageQuotaSerializer(quota)
    return Response(serializer.data)
