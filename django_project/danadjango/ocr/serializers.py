import base64
from rest_framework import serializers
from .models import Language, OCRRequest, OCRSettings, RecognitionHistory


class LanguageSerializer(serializers.ModelSerializer):
    """Сериализатор языков"""
    
    class Meta:
        model = Language
        fields = ['id', 'code', 'name', 'name_en', 'is_active']


class OCRRequestSerializer(serializers.ModelSerializer):
    """Сериализатор OCR запросов"""
    
    user = serializers.StringRelatedField(read_only=True)
    language_name = serializers.CharField(source='language.name', read_only=True)
    
    class Meta:
        model = OCRRequest
        fields = [
            'id',
            'user',
            'image',
            'language',
            'language_name',
            'recognized_text',
            'status',
            'confidence',
            'processing_time',
            'error_message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'recognized_text',
            'status',
            'confidence',
            'processing_time',
            'error_message',
            'created_at',
            'updated_at',
        ]


class OCRRequestCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания OCR запроса"""
    
    class Meta:
        model = OCRRequest
        fields = ['image', 'language']
    
    def validate_image(self, value):
        """Валидация изображения"""
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Размер файла не должен превышать 10MB. Ваш файл: {value.size / 1024 / 1024:.2f}MB"
            )
        
        valid_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
        ext = value.name.split('.')[-1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                f"Недопустимое расширение файла. Разрешены: {', '.join(valid_extensions)}"
            )
        
        return value


class OCRSettingsSerializer(serializers.ModelSerializer):
    """Сериализатор настроек OCR"""
    
    class Meta:
        model = OCRSettings
        fields = ['id', 'key', 'value', 'description', 'updated_at']
        read_only_fields = ['updated_at']


class RecognitionHistorySerializer(serializers.ModelSerializer):
    """Сериализатор истории распознавания"""
    
    class Meta:
        model = RecognitionHistory
        fields = [
            'id',
            'original_image_url',
            'original_image',
            'recognized_text',
            'language',
            'confidence',
            'is_favorite',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RecognitionHistoryCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания записи истории"""
    
    class Meta:
        model = RecognitionHistory
        fields = [
            'original_image_url',
            'original_image',
            'recognized_text',
            'language',
            'confidence',
        ]


class OCRRecognizeSerializer(serializers.Serializer):
    """Сериализатор для распознавания текста"""
    
    image = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Base64 строка изображения (если не используется multipart/form-data)"
    )
    language = serializers.ChoiceField(
        choices=['kk', 'ru', 'en'],
        required=False,
        default='ru',
        help_text="Код языка (kk, ru, en). Если не указан, будет автоопределение"
    )
    
    def validate(self, attrs):
        """Валидация - image должен быть предоставлен либо как поле, либо как файл"""
        return attrs
