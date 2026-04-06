from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, time
from metapko.models import Teacher, Course, StudyGroup, Room, Department, StudyProgram, Building
from scheduler.models import TeacherProfile, CourseProfile, GroupProfile

class Command(BaseCommand):
    help = 'Заполнение базы данных тестовыми данными для демонстрации планировщика.'

    def handle(self, *args, **options):
        self.stdout.write('Запуск сидирования данных...')

        # 1. Создаем Кафедру и Корпус
        dept, _ = Department.objects.get_or_create(name='Кафедра Информационных Технологий', code='КИТ')
        build, _ = Building.objects.get_or_create(name='Главный корпус', code='ГК', address='пр. Абая, 1')
        prog, _ = StudyProgram.objects.get_or_create(name='Информационные системы', code='ИС')

        # 2. Создаем Аудитории
        Room.objects.get_or_create(building=build, name='101', capacity=30)
        Room.objects.get_or_create(building=build, name='102', capacity=20)
        Room.objects.get_or_create(building=build, name='Компьютерный класс', capacity=15)

        # 3. Создаем Преподавателей
        t1, _ = Teacher.objects.get_or_create(full_name='Ахметов Серик Болатович', department=dept, position='Профессор')
        t2, _ = Teacher.objects.get_or_create(full_name='Иванова Елена Петровна', department=dept, position='Старший преподаватель')

        TeacherProfile.objects.get_or_create(teacher=t1, max_load_hours=18)
        TeacherProfile.objects.get_or_create(teacher=t2, max_load_hours=24)

        # 4. Создаем Группы
        g1, _ = StudyGroup.objects.get_or_create(name='ИС-21', program=prog, intake_year=2021)
        g2, _ = StudyGroup.objects.get_or_create(name='ИС-22', program=prog, intake_year=2022)

        GroupProfile.objects.get_or_create(group=g1, student_count=25)
        GroupProfile.objects.get_or_create(group=g2, student_count=18)

        # 5. Создаем Курсы
        c1, _ = Course.objects.get_or_create(title='Базы данных', code='BD101')
        c2, _ = Course.objects.get_or_create(title='Программирование Python', code='PY202')
        c3, _ = Course.objects.get_or_create(title='Алгоритмы и структуры данных', code='ASD303')

        c1.study_groups.add(g1)
        c2.study_groups.add(g1, g2)
        c3.study_groups.add(g2)

        # Профили курсов
        cp1, _ = CourseProfile.objects.get_or_create(course=c1, target_hours=4, course_type='lecture')
        cp2, _ = CourseProfile.objects.get_or_create(course=c2, target_hours=6, course_type='practice')
        cp3, _ = CourseProfile.objects.get_or_create(course=c3, target_hours=4, course_type='lecture')

        # Специализации (связываем преподавателей с курсами)
        t1.scheduler_profile.specializations.add(c1, c3)
        t2.scheduler_profile.specializations.add(c2)

        self.stdout.write(self.style.SUCCESS('Данные успешно загружены!'))
