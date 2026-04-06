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

        # 2. Получаем все курсы, требующие распределения
        courses = Course.objects.filter(is_active=True).order_by('title')
        
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

            # Ищем подходящего преподавателя
            # Сначала тех, у кого этот курс в специализации
            potential_teachers = teachers.filter(scheduler_profile__specializations=course)
            
            if not potential_teachers.exists():
                # Если нет узких специалистов, берем всех из его кафедры (если есть)
                if course.teacher: # Если уже назначен статически в metapko
                    potential_teachers = [course.teacher]
                else:
                    # Логируем конфликт: нет специалистов
                    self.log_conflict('warning', f"Для курса '{course.title}' не найдено специалистов в TeacherProfile.")
                    potential_teachers = teachers.all()

            for teacher in potential_teachers:
                t_profile = teacher.scheduler_profile
                
                # Считаем текущую подтвержденную нагрузку + то что уже накидали в этом цикле
                current_load = AssignmentResult.objects.filter(teacher=teacher).aggregate(total=Sum('course__scheduler_profile__target_hours'))['total'] or 0
                
                if current_load + hours <= t_profile.max_load_hours:
                    AssignmentResult.objects.create(
                        course=course,
                        teacher=teacher,
                        is_confirmed=False
                    )
                    assigned = True
                    break
            
            if not assigned:
                self.log_conflict('error', f"Не удалось распределить курс '{course.title}': все подходящие преподаватели перегружены.")

        return self.conflicts

    def log_conflict(self, severity, message):
        conflict = ScheduleConflict.objects.create(severity=severity, message=message)
        self.conflicts.append(conflict)
