# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('recognition_text', models.TextField(blank=True, help_text='Текст из OCR, который обсуждается', null=True, verbose_name='Распознанный текст')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_sessions', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Сессия чата',
                'verbose_name_plural': 'Сессии чата',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('user', 'Пользователь'), ('assistant', 'AI Ассистент')], max_length=20, verbose_name='Роль')),
                ('content', models.TextField(verbose_name='Содержимое')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='ai_assistant.chatsession', verbose_name='Сессия')),
            ],
            options={
                'verbose_name': 'Сообщение чата',
                'verbose_name_plural': 'Сообщения чата',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIUsageQuota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('daily_questions_used', models.IntegerField(default=0, verbose_name='Использовано вопросов сегодня')),
                ('last_reset_date', models.DateField(auto_now_add=True, verbose_name='Дата последнего сброса')),
                ('total_questions_asked', models.IntegerField(default=0, verbose_name='Всего вопросов задано')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ai_quota', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Квота AI',
                'verbose_name_plural': 'Квоты AI',
            },
        ),
    ]
