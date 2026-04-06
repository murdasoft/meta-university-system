from django.test import TestCase
from metapko.models import Teacher, Course, StudyGroup, Room, Department, StudyProgram, Building
from scheduler.models import TeacherProfile, CourseProfile, GroupProfile, AssignmentResult, ScheduleConflict
from scheduler.logic.distributor import LoadDistributor
from scheduler.logic.scheduler import ScheduleGenerator
from django.utils import timezone
from datetime import timedelta

class SchedulerLogicTests(TestCase):
    def setUp(self):
        # Подготовка тестовых данных
        self.dept = Department.objects.create(name='IT', code='IT')
        self.t1 = Teacher.objects.create(full_name='Test Teacher 1', department=self.dept)
        self.t2 = Teacher.objects.create(full_name='Test Teacher 2', department=self.dept)
        
        self.tp1 = TeacherProfile.objects.create(teacher=self.t1, max_load_hours=10)
        self.tp2 = TeacherProfile.objects.create(teacher=self.t2, max_load_hours=20)
        
        self.c1 = Course.objects.create(title='Course 1', code='C1')
        self.c2 = Course.objects.create(title='Course 2', code='C2')
        self.c3 = Course.objects.create(title='Course 3', code='C3')
        
        self.cp1 = CourseProfile.objects.create(course=self.c1, target_hours=8)
        self.cp2 = CourseProfile.objects.create(course=self.c2, target_hours=8)
        self.cp3 = CourseProfile.objects.create(course=self.c3, target_hours=8)

        # Установка специализаций
        self.tp1.specializations.add(self.c1, self.c2)
        self.tp2.specializations.add(self.c2, self.c3)

        # Данные для расписания
        self.building = Building.objects.create(name='Main', code='M')
        self.room = Room.objects.create(name='101', building=self.building, capacity=30)
        
        self.prog = StudyProgram.objects.create(name='Prog', code='P')
        self.group = StudyGroup.objects.create(name='G1', program=self.prog, intake_year=2023)
        self.gp = GroupProfile.objects.create(group=self.group, student_count=20)
        
        self.c1.study_groups.add(self.group)

    def test_load_distributor_greedy(self):
        distributor = LoadDistributor()
        conflicts = distributor.distribute()
        
        # c1 требует 8 часов. tp1 может взять. tp1 остаток: 2 часа.
        # c2 требует 8 часов. tp1 не может (8+8 > 10). tp2 может (у него 20 часов).
        # c3 требует 8 часов. tp2 может взять (8+8 <= 20).
        
        # Проверяем, что распределено 3 курса
        self.assertEqual(AssignmentResult.objects.count(), 3)
        
        # tp1 не должен превышать свои 10 часов
        load_t1 = sum(a.course.scheduler_profile.target_hours for a in AssignmentResult.objects.filter(teacher=self.t1))
        self.assertLessEqual(load_t1, self.tp1.max_load_hours)
        
        # tp2 не должен превышать 20 часов
        load_t2 = sum(a.course.scheduler_profile.target_hours for a in AssignmentResult.objects.filter(teacher=self.t2))
        self.assertLessEqual(load_t2, self.tp2.max_load_hours)

    def test_schedule_generator_no_overlapping(self):
        # Выполняем распределение
        LoadDistributor().distribute()
        
        generator = ScheduleGenerator(start_date=timezone.now().date())
        generator.generate()
        
        # Проверяем сессии
        from metapko.models import ClassSession
        sessions = ClassSession.objects.filter(course=self.c1)
        self.assertTrue(sessions.exists())
        
        # Проверка, что для одной группы нет пересекающихся занятий
        group_sessions = ClassSession.objects.filter(course__study_groups=self.group)
        times = [(s.starts_at, s.ends_at) for s in group_sessions]
        
        # Сортируем и проверяем пересечения
        times.sort(key=lambda x: x[0])
        for i in range(len(times) - 1):
            self.assertLessEqual(times[i][1], times[i+1][0], "Обнаружено наложение занятий для одной группы!")

    def test_overload_conflict(self):
        # Создаем курс без преподавателей со специализацией
        c4 = Course.objects.create(title='Course 4', code='C4')
        CourseProfile.objects.create(course=c4, target_hours=50) # Слишком большое количество часов
        
        distributor = LoadDistributor()
        conflicts = distributor.distribute()
        
        # Должен быть конфликт
        self.assertTrue(any("перегружены" in c.message or "не найдено специалистов" in c.message for c in conflicts))
