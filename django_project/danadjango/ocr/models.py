from django.db import models
from django.conf import settings


class Language(models.Model):
    """Модель языков для OCR"""
    
    code = models.CharField(
        max_length=5,
        unique=True,
        verbose_name='Код языка'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Название языка'
    )
    name_en = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Название на английском'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    
    class Meta:
        verbose_name = 'Язык'
        verbose_name_plural = 'Языки'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class OCRRequest(models.Model):
    """Модель запросов на распознавание текста"""
    
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('processing', 'Обрабатывается'),
        ('completed', 'Завершено'),
        ('failed', 'Ошибка'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ocr_requests',
        verbose_name='Пользователь'
    )
    image = models.ImageField(
        upload_to='ocr_images/%Y/%m/%d/',
        verbose_name='Изображение'
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ocr_requests',
        verbose_name='Язык'
    )
    recognized_text = models.TextField(
        blank=True,
        verbose_name='Распознанный текст'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    confidence = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Точность распознавания'
    )
    processing_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Время обработки (сек)'
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='Сообщение об ошибке'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'OCR запрос'
        verbose_name_plural = 'OCR запросы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OCR запрос #{self.id} - {self.user.username} ({self.get_status_display()})"


class OCRSettings(models.Model):
    """Модель настроек OCR"""
    
    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Ключ настройки'
    )
    value = models.TextField(
        verbose_name='Значение'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Настройка OCR'
        verbose_name_plural = 'Настройки OCR'
    
    def __str__(self):
        return self.key


class RecognitionHistory(models.Model):
    """Модель истории распознавания текста"""
    
    LANGUAGE_CHOICES = [
        ('kk', 'Қазақ тілі'),
        ('ru', 'Русский'),
        ('en', 'English'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recognition_history',
        verbose_name='Пользователь'
    )
    original_image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='URL оригинального изображения'
    )
    original_image = models.ImageField(
        upload_to='recognition_images/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Оригинальное изображение'
    )
    recognized_text = models.TextField(
        verbose_name='Распознанный текст'
    )
    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        verbose_name='Язык'
    )
    confidence = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Точность распознавания'
    )
    is_favorite = models.BooleanField(
        default=False,
        verbose_name='Избранное'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'История распознавания'
        verbose_name_plural = 'История распознаваний'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['language']),
            models.Index(fields=['is_favorite']),
        ]
    
    def __str__(self):
        return f"История #{self.id} - {self.user.email} ({self.language})"
