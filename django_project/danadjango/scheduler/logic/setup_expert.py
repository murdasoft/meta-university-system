from metapko.models import Teacher, Course, StudyGroup
from scheduler.models import TeacherProfile, CourseProfile, GroupProfile

class SetupExpert:
    @staticmethod
    def fill_missing_profiles():
        """
        Автоматически создает отсутствующие профили для учителей, курсов и групп.
        Использует случайные, но логичные значения для демо-режима.
        """
        stats = {'teachers': 0, 'courses': 0, 'groups': 0}
        
        # 1. Учителя
        for teacher in Teacher.objects.filter(scheduler_profile__isnull=True):
            # Распределяем степени в зависимости от должности
            degree = TeacherProfile.Degree.NONE
            if 'профессор' in teacher.position.lower() or 'доцент' in teacher.position.lower():
                degree = TeacherProfile.Degree.DOCTOR
            elif 'старший преподаватель' in teacher.position.lower():
                degree = TeacherProfile.Degree.CANDIDATE
            
            TeacherProfile.objects.create(
                teacher=teacher,
                academic_degree=degree,
                employment_rate=1.0
            )
            stats['teachers'] += 1
            
        # 2. Курсы
        for course in Course.objects.filter(scheduler_profile__isnull=True):
            CourseProfile.objects.create(
                course=course,
                target_hours=32,
                course_type=CourseProfile.CourseType.LECTURE if 'лекц' in course.title.lower() else CourseProfile.CourseType.PRACTICE
            )
            stats['courses'] += 1
            
        # 3. Группы
        for group in StudyGroup.objects.filter(scheduler_profile__isnull=True):
            GroupProfile.objects.create(
                group=group,
                student_count=25
            )
            stats['groups'] += 1
            
        return stats
