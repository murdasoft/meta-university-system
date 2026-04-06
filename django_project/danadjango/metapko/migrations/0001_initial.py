# Generated manually for metapko.IntegrationClient

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='IntegrationClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='название')),
                ('is_active', models.BooleanField(default=True, verbose_name='активен')),
                ('key_hash', models.CharField(db_index=True, editable=False, max_length=64, verbose_name='хеш ключа')),
                ('notes', models.TextField(blank=True, verbose_name='заметки')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='создан')),
                ('last_used_at', models.DateTimeField(blank=True, null=True, verbose_name='последнее использование')),
            ],
            options={
                'verbose_name': 'клиент интеграции',
                'verbose_name_plural': 'клиенты интеграции',
                'ordering': ['-created_at'],
            },
        ),
    ]
