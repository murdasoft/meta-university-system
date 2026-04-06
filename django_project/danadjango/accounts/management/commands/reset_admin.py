from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Сброс пароля администратора на admin123'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='admin')
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('✓ Пароль admin сброшен на: admin123'))
        except User.DoesNotExist:
            User.objects.create_superuser(
                username='admin',
                email='admin@qazaqdana.local',
                password='admin123',
                role='admin',
                first_name='Администратор',
                last_name='Системы'
            )
            self.stdout.write(self.style.SUCCESS('✓ Создан администратор admin:admin123'))
