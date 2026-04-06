from django.db import models
from django.conf import settings
import uuid


class ChatSession(models.Model):
    """Сессия чата с AI"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        verbose_name='Пользователь'
    )
    recognition_text = models.TextField(
        blank=True,
        null=True,
        verbose_name='Распознанный текст',
        help_text='Текст из OCR, который обсуждается'
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
        verbose_name = 'Сессия чата'
        verbose_name_plural = 'Сессии чата'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Чат {self.user.email} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"


class ChatMessage(models.Model):
    """Сообщение в чате"""
    
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('assistant', 'AI Ассистент'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Сессия'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='Роль'
    )
    content = models.TextField(
        verbose_name='Содержимое'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чата'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:50]}..."


class AIUsageQuota(models.Model):
    """Квота использования AI для пользователя"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_quota',
        verbose_name='Пользователь'
    )
    daily_questions_used = models.IntegerField(
        default=0,
        verbose_name='Использовано вопросов сегодня'
    )
    last_reset_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата последнего сброса'
    )
    total_questions_asked = models.IntegerField(
        default=0,
        verbose_name='Всего вопросов задано'
    )
    
    class Meta:
        verbose_name = 'Квота AI'
        verbose_name_plural = 'Квоты AI'
    
    def __str__(self):
        return f"{self.user.email} - {self.daily_questions_used} вопросов сегодня"
    
    def reset_if_needed(self):
        """Сбросить счётчик если новый день"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.last_reset_date < today:
            self.daily_questions_used = 0
            self.last_reset_date = today
            self.save()
    
    def can_ask_question(self):
        """Проверить, может ли пользователь задать вопрос"""
        self.reset_if_needed()
        
        # Premium пользователи - unlimited
        if hasattr(self.user, 'subscription_type') and self.user.subscription_type == 'premium':
            return True, None
        
        # Free пользователи - 5 вопросов в день
        FREE_DAILY_LIMIT = 5
        
        if self.daily_questions_used >= FREE_DAILY_LIMIT:
            return False, f"Достигнут дневной лимит ({FREE_DAILY_LIMIT} вопросов). Обновитесь до Premium для unlimited доступа."
        
        return True, None
    
    def increment_usage(self):
        """Увеличить счётчик использования"""
        self.reset_if_needed()
        self.daily_questions_used += 1
        self.total_questions_asked += 1
        self.save()
