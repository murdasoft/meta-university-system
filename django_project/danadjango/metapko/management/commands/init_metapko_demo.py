from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from metapko.models import (
    ClassSession,
    Course,
    Department,
    FaqEntry,
    IikoOutlet,
    MenuItem,
    Teacher,
)


class Command(BaseCommand):
    help = 'Загрузить демо-данные Meta-университет + IIKO (mock) в metapko'

    def handle(self, *args, **options):
        if Department.objects.exists():
            self.stdout.write(self.style.WARNING('Данные metapko уже есть — пропуск (удалите вручную при необходимости).'))
            return

        dep_it = Department.objects.create(name='Кафедра информационных систем', code='ИС', sort_order=1)
        dep_mgmt = Department.objects.create(name='Кафедра управления и сервиса', code='УИС', sort_order=2)

        t1 = Teacher.objects.create(
            full_name='Әлия Серікқызы Нұрланова',
            department=dep_it,
            position='доцент',
            email='teacher.is@meta-uni.local',
            phone='+7 700 000 00 01',
        )
        t2 = Teacher.objects.create(
            full_name='Ерлан Болатұлы Омаров',
            department=dep_mgmt,
            position='ст. преподаватель',
            email='teacher.mgmt@meta-uni.local',
        )

        c1 = Course.objects.create(
            title='Интеграция информационных систем',
            code='ИС-405',
            description='API, шлюзы, боты в образовательной среде.',
            teacher=t1,
        )
        c2 = Course.objects.create(
            title='Управление сервисами общественного питания',
            code='УП-210',
            description='Процессы ресторана, связь с IIKO (концептуально).',
            teacher=t2,
        )

        now = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        ClassSession.objects.create(
            course=c1,
            title='REST API и безопасность',
            teacher=t1,
            starts_at=now + timedelta(days=1),
            ends_at=now + timedelta(days=1, hours=1, minutes=30),
            room='А-204',
        )
        ClassSession.objects.create(
            course=c2,
            title='Организация зала и кассовые сценарии',
            teacher=t2,
            starts_at=now + timedelta(days=2),
            ends_at=now + timedelta(days=2, hours=2),
            room='Б-101',
        )

        FaqEntry.objects.create(
            question='Где посмотреть расписание через бота?',
            answer='После подключения бота используйте команды, которые запрашивают /api/metapko/v1/class-sessions/ с фильтрами по датам.',
            keywords='расписание, бот, занятия',
            sort_order=1,
        )
        FaqEntry.objects.create(
            question='Что такое «точка IIKO» в системе?',
            answer='Это наша упрощённая модель филиала/ресторана для учебного контура; реальная IIKO подключается отдельно по их API.',
            keywords='iiko, точка, ресторан',
            sort_order=2,
        )

        outlet = IikoOutlet.objects.create(
            name='Столовая Meta-университет',
            address='г. Алматы, учебный корпус',
            phone='+7 727 000 00 00',
        )
        MenuItem.objects.create(
            outlet=outlet,
            name='Комплекс обеденный №1',
            category='Комплексы',
            price=Decimal('1290.00'),
            sort_order=1,
        )
        MenuItem.objects.create(
            outlet=outlet,
            name='Чай чёрный 200 мл',
            category='Напитки',
            price=Decimal('150.00'),
            sort_order=2,
        )

        self.stdout.write(self.style.SUCCESS('Демо-данные metapko созданы.'))
