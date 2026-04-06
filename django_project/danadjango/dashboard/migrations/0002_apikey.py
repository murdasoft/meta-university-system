# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название ключа')),
                ('key_type', models.CharField(choices=[('google_vision', 'Google Vision API'), ('google_vision_json', 'Google Vision API (JSON файл)'), ('other', 'Другой API ключ')], default='other', max_length=50, verbose_name='Тип ключа')),
                ('api_key', models.TextField(blank=True, help_text='Для текстовых ключей', null=True, verbose_name='API ключ (текст)')),
                ('json_file', models.FileField(blank=True, help_text='Для Google Vision API JSON файлов', null=True, upload_to='api_keys/', verbose_name='JSON файл')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
            ],
            options={
                'verbose_name': 'API ключ',
                'verbose_name_plural': 'API ключи',
                'ordering': ['-created_at'],
            },
        ),
    ]
