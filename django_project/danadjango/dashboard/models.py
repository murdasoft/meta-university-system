from django.db import models
from django.conf import settings


class APIKey(models.Model):
    """Модель для хранения API ключей"""
    
    KEY_TYPE_CHOICES = [
        ('google_vision', 'Google Vision API'),
        ('openai', 'OpenAI (ChatGPT-4 Vision)'),
        ('other', 'Другой API ключ'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название ключа'
    )
    key_type = models.CharField(
        max_length=50,
        choices=KEY_TYPE_CHOICES,
        default='google_vision',
        verbose_name='Тип ключа'
    )
    api_key = models.TextField(
        verbose_name='API ключ',
        help_text='Вставьте ваш API ключ'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
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
        verbose_name = 'API ключ'
        verbose_name_plural = 'API ключи'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_key_type_display()})"
    
    def get_key_value(self):
        """Получить значение ключа"""
        return self.api_key
