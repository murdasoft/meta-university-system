# После ветки 0004: убрать json_file и привести api_key к модели без null (как было в simplify_apikey)

from django.db import migrations, models


def null_api_key_to_empty(apps, schema_editor):
    APIKey = apps.get_model('dashboard', 'APIKey')
    APIKey.objects.filter(api_key__isnull=True).update(api_key='')


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_add_openai_key_type'),
    ]

    operations = [
        migrations.RunPython(null_api_key_to_empty, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='apikey',
            name='json_file',
        ),
        migrations.AlterField(
            model_name='apikey',
            name='api_key',
            field=models.TextField(help_text='Вставьте ваш API ключ', verbose_name='API ключ'),
        ),
    ]
