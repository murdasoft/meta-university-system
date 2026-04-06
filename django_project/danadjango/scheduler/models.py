from django.db import models
from metapko.models import Teacher, Course, StudyGroup, Room

class TeacherProfile(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='scheduler_profile')
    max_load_hours = models.PositiveIntegerField('Максимальная нагрузка', default=20)
    specializations = models.ManyToManyField(Course, blank=True)

    def __str__(self):
        return f"Профиль: {self.teacher.full_name}"

class CourseProfile(models.Model):
    class CourseType(models.TextChoices):
        LECTURE = 'lecture', 'Лекция'
        PRACTICE = 'practice', 'Практика'
        LAB = 'lab', 'Лабораторная'

    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='scheduler_profile')
    target_hours = models.PositiveIntegerField('Часов в семестре', default=32)
    course_type = models.CharField('Тип', max_length=20, choices=CourseType.choices, default=CourseType.LECTURE)

    def __str__(self):
        return f"{self.course.title} ({self.get_course_type_display()})"

class GroupProfile(models.Model):
    group = models.OneToOneField(StudyGroup, on_delete=models.CASCADE, related_name='scheduler_profile')
    student_count = models.PositiveIntegerField('Студентов', default=20)

    def __str__(self):
        return f"Группа: {self.group.name}"

class AssignmentResult(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ScheduleConflict(models.Model):
    severity = models.CharField(max_length=20, choices=[('error', 'Ошибка'), ('warning', 'Предупреждение')])
    message = models.TextField()
    context = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
