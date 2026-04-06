# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ocr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='name_en',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Название на английском'),
        ),
    ]
