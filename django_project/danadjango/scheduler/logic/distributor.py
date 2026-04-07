from django.db.models import Sum
from metapko.models import Teacher, Course
from scheduler.models import TeacherProfile, CourseProfile, AssignmentResult, ScheduleConflict

class LoadDistributor:
    def __init__(self):
        self.conflicts = []

    def distribute(self):
        """
        Автоматическое распределение дисциплин по преподавателям.
        """
        # 1. Очищаем старые неподтвержденные результаты
        AssignmentResult.objects.filter(is_confirmed=False).delete()
        ScheduleConflict.objects.all().delete()

        # 2. Получаем курсы, у которых ЕЩЕ НЕТ закрепленного преподавателя
        assigned_course_ids = AssignmentResult.objects.values_list('course_id', flat=True)
        courses = Course.objects.filter(is_active=True).exclude(id__in=assigned_course_ids).order_by('title')
        
        # 3. Получаем всех активных преподавателей с профилями
        teachers = Teacher.objects.filter(is_active=True, scheduler_profile__isnull=False)

        for course in courses:
            # Ищем профиль курса для понимания нагрузки
            try:
                c_profile = course.scheduler_profile
            except CourseProfile.DoesNotExist:
                # Если профиля нет, создаем дефолтный
                c_profile = CourseProfile.objects.create(course=course, target_hours=32)
            
            hours = c_profile.target_hours
            assigned = False

            # Фильтруем подходящих преподавателей
            potential_teachers = teachers.all()
            
            # Приоритезация по специализации
            specialists = potential_teachers.filter(scheduler_profile__specializations=course)
            if specialists.exists():
                potential_teachers = specialists

            # Сортировка по степени, если это лекция
            if c_profile.course_type == CourseProfile.CourseType.LECTURE:
                # Очередность: research_prof, professor, assoc_prof, phd, master, none
                degree_order = {
                    'research_prof': 0, 
                    'professor': 1, 
                    'assoc_prof': 2, 
                    'phd': 3, 
                    'master': 4, 
                    'none': 5
                }
                potential_teachers = sorted(
                    potential_teachers, 
                    key=lambda t: degree_order.get(t.scheduler_profile.academic_degree, 5)
                )

            for teacher in potential_teachers:
                t_profile = teacher.scheduler_profile
                
                # РАСЧЕТ: 32 часа в семестр = 2 часа в неделю (пара 2 часа * 1 раз в неделю)
                weekly_hours = hours / 16.0 
                
                # Считаем уже назначенную недельную нагрузку
                results = AssignmentResult.objects.filter(teacher=teacher)
                current_weekly_load = 0
                for r in results:
                    if hasattr(r.course, 'scheduler_profile'):
                        current_weekly_load += (r.course.scheduler_profile.target_hours / 16.0)
                
                if current_weekly_load + weekly_hours <= t_profile.max_load_hours:
                    # 1. Создаем результат планировщика
                    AssignmentResult.objects.create(
                        course=course,
                        teacher=teacher,
                        is_confirmed=False
                    )
                    # 2. СИНХРОНИЗАЦИЯ: прописываем учителя в основной модели курса
                    course.teacher = teacher
                    course.save()
                    
                    assigned = True
                    break
            
            if not assigned:
                self.log_conflict('error', f"Не удалось распределить курс '{course.title}': нет свободных преподавателей с нужной квалификацией.")

        return self.conflicts

    def log_conflict(self, severity, message):
        conflict = ScheduleConflict.objects.create(severity=severity, message=message)
        self.conflicts.append(conflict)
