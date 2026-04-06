from django.contrib import admin
from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'key_type',
        'is_active',
        'created_at',
        'updated_at'
    ]
    list_filter = ['key_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'key_type', 'description', 'is_active')
        }),
        ('Ключ', {
            'fields': ('api_key', 'json_file')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
