from rest_framework import serializers
from .models import ChatSession, ChatMessage, AIUsageQuota


class ChatMessageSerializer(serializers.ModelSerializer):
    """Сериализатор для сообщений чата"""
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Сериализатор для сессий чата"""
    
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'recognition_text', 'created_at', 'updated_at', 'messages', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class ChatRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса к AI чату"""
    
    message = serializers.CharField(
        required=True,
        help_text='Сообщение пользователя'
    )
    session_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text='ID сессии чата (если продолжаем существующий чат)'
    )
    recognition_text = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text='Распознанный текст (контекст для AI)'
    )
    language = serializers.ChoiceField(
        choices=['ru', 'kk', 'en'],
        default='ru',
        help_text='Язык ответа'
    )


class QuickActionSerializer(serializers.Serializer):
    """Сериализатор для быстрых действий с текстом"""
    
    action = serializers.ChoiceField(
        choices=[
            'translate_ru',
            'translate_kk', 
            'translate_en',
            'correct',
            'summarize',
            'explain'
        ],
        required=True,
        help_text='Тип действия'
    )
    text = serializers.CharField(
        required=True,
        help_text='Текст для обработки'
    )
    language = serializers.ChoiceField(
        choices=['ru', 'kk', 'en'],
        default='ru',
        help_text='Язык ответа'
    )


class AIUsageQuotaSerializer(serializers.ModelSerializer):
    """Сериализатор для квоты использования AI"""
    
    can_ask = serializers.SerializerMethodField()
    remaining_questions = serializers.SerializerMethodField()
    is_premium = serializers.SerializerMethodField()
    
    class Meta:
        model = AIUsageQuota
        fields = [
            'daily_questions_used',
            'total_questions_asked',
            'last_reset_date',
            'can_ask',
            'remaining_questions',
            'is_premium'
        ]
        read_only_fields = ['daily_questions_used', 'total_questions_asked', 'last_reset_date']
    
    def get_can_ask(self, obj):
        can_ask, _ = obj.can_ask_question()
        return can_ask
    
    def get_remaining_questions(self, obj):
        obj.reset_if_needed()
        
        # Premium - unlimited
        if hasattr(obj.user, 'subscription_type') and obj.user.subscription_type == 'premium':
            return -1  # -1 означает unlimited
        
        # Free - 5 в день
        FREE_DAILY_LIMIT = 5
        return max(0, FREE_DAILY_LIMIT - obj.daily_questions_used)
    
    def get_is_premium(self, obj):
        return hasattr(obj.user, 'subscription_type') and obj.user.subscription_type == 'premium'
