from django.core.management.base import BaseCommand
from ocr.models import Language, OCRSettings


class Command(BaseCommand):
    help = 'Инициализация языков и настроек OCR'

    def handle(self, *args, **options):
        self.stdout.write('Инициализация языков и настроек OCR...')
        
        # Создание языков
        languages = [
            {'code': 'ru', 'name': 'Русский', 'name_en': 'Russian'},
            {'code': 'kk', 'name': 'Қазақ тілі', 'name_en': 'Kazakh'},
            {'code': 'en', 'name': 'English', 'name_en': 'English'},
        ]
        
        for lang_data in languages:
            language, created = Language.objects.get_or_create(
                code=lang_data['code'],
                defaults={
                    'name': lang_data['name'],
                    'name_en': lang_data.get('name_en', lang_data['name']),
                    'is_active': True
                }
            )
            if not created:
                # Обновляем name_en если его нет
                if not language.name_en:
                    language.name_en = lang_data.get('name_en', lang_data['name'])
                    language.save()
                    self.stdout.write(self.style.SUCCESS(f'✓ Обновлен язык: {language.name} (добавлен name_en)'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠ Язык {language.name} уже существует'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✓ Создан язык: {language.name}'))
        
        # Создание настроек
        settings = [
            {
                'key': 'max_image_size',
                'value': '10485760',  # 10MB в байтах
                'description': 'Максимальный размер загружаемого изображения в байтах'
            },
            {
                'key': 'supported_formats',
                'value': 'jpg,jpeg,png,bmp,tiff',
                'description': 'Поддерживаемые форматы изображений'
            },
            {
                'key': 'default_language',
                'value': 'ru',
                'description': 'Язык распознавания по умолчанию'
            },
        ]
        
        for setting_data in settings:
            setting, created = OCRSettings.objects.get_or_create(
                key=setting_data['key'],
                defaults={
                    'value': setting_data['value'],
                    'description': setting_data['description']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Создана настройка: {setting.key}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠ Настройка {setting.key} уже существует'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Инициализация языков и настроек OCR завершена!'))
