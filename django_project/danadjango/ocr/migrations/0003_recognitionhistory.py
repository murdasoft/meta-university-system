# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ocr', '0002_language_name_en'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecognitionHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_image_url', models.URLField(blank=True, max_length=500, null=True, verbose_name='URL оригинального изображения')),
                ('original_image', models.ImageField(blank=True, null=True, upload_to='recognition_images/%Y/%m/%d/', verbose_name='Оригинальное изображение')),
                ('recognized_text', models.TextField(verbose_name='Распознанный текст')),
                ('language', models.CharField(choices=[('kk', 'Қазақ тілі'), ('ru', 'Русский'), ('en', 'English')], max_length=5, verbose_name='Язык')),
                ('confidence', models.FloatField(blank=True, null=True, verbose_name='Точность распознавания')),
                ('is_favorite', models.BooleanField(default=False, verbose_name='Избранное')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recognition_history', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'История распознавания',
                'verbose_name_plural': 'История распознаваний',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='recognitionhistory',
            index=models.Index(fields=['user', '-created_at'], name='ocr_recogn_user_id_created_idx'),
        ),
        migrations.AddIndex(
            model_name='recognitionhistory',
            index=models.Index(fields=['language'], name='ocr_recogn_language_idx'),
        ),
        migrations.AddIndex(
            model_name='recognitionhistory',
            index=models.Index(fields=['is_favorite'], name='ocr_recogn_is_favor_idx'),
        ),
    ]
