# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_delete_dashboardstats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apikey',
            name='key_type',
            field=models.CharField(
                choices=[
                    ('google_vision', 'Google Vision API'),
                    ('openai', 'OpenAI (ChatGPT-4 Vision)'),
                    ('other', 'Другой API ключ')
                ],
                default='google_vision',
                max_length=50,
                verbose_name='Тип ключа'
            ),
        ),
    ]
