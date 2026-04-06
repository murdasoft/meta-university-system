from django.contrib import admin
from .models import Language, OCRRequest, OCRSettings


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(OCRRequest)
class OCRRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'language', 'status', 'confidence', 'created_at']
    list_filter = ['status', 'language', 'created_at']
    search_fields = ['user__username', 'recognized_text']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'image', 'language', 'status')
        }),
        ('Результаты распознавания', {
            'fields': ('recognized_text', 'confidence', 'processing_time')
        }),
        ('Ошибки', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OCRSettings)
class OCRSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'updated_at']
    search_fields = ['key', 'value']
    readonly_fields = ['updated_at']
