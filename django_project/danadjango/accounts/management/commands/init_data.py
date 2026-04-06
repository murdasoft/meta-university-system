from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Инициализация базовых данных приложения'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем инициализацию базовых данных...')
        
        # Создание суперпользователя-администратора
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@meta-university.local',
                password='admin123',
                role='admin',
                first_name='Администратор',
                last_name='Системы'
            )
            self.stdout.write(self.style.SUCCESS('✓ Создан суперпользователь admin:admin123'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Суперпользователь admin уже существует'))
        
        # Создание тестового пользователя
        if not User.objects.filter(username='testuser').exists():
            User.objects.create_user(
                username='testuser',
                email='test@meta-university.local',
                password='test123',
                role='user',
                first_name='Тестовый',
                last_name='Пользователь'
            )
            self.stdout.write(self.style.SUCCESS('✓ Создан тестовый пользователь testuser:test123'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Тестовый пользователь testuser уже существует'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Инициализация базовых данных завершена!'))
