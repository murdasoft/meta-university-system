from django.contrib import admin
from .models import ChatSession, ChatMessage, AIUsageQuota


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'message_count']
    list_filter = ['created_at']
    search_fields = ['user__email', 'recognition_text']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Сообщений'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'role', 'content_preview', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['content', 'session__user__email']
    readonly_fields = ['id', 'created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Содержимое'


@admin.register(AIUsageQuota)
class AIUsageQuotaAdmin(admin.ModelAdmin):
    list_display = ['user', 'daily_questions_used', 'total_questions_asked', 'last_reset_date']
    list_filter = ['last_reset_date']
    search_fields = ['user__email']
    readonly_fields = ['total_questions_asked']
