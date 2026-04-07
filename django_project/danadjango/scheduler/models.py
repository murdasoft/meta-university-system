from django.db import models
from metapko.models import Teacher, Course, StudyGroup, Room

class TeacherProfile(models.Model):
    class Degree(models.TextChoices):
        NONE = 'none', 'Без степени'
        MASTER = 'master', 'Магистр'
        CANDIDATE = 'candidate', 'Кандидат наук'
        DOCTOR = 'doctor', 'Доктор наук'
        PHD = 'phd', 'PhD'

    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='scheduler_profile')
    academic_degree = models.CharField('Ученая степень', max_length=20, choices=Degree.choices, default=Degree.NONE)
    employment_rate = models.DecimalField('Ставка', max_digits=3, decimal_places=2, default=1.0)
    max_load_hours = models.PositiveIntegerField('Максимальная нагрузка (ч/нед)', default=20)
    specializations = models.ManyToManyField(Course, blank=True)

    def save(self, *args, **kwargs):
        # Автоматический пересчет часов на основе ставки (база: 20 часов = 1.0 ставка)
        self.max_load_hours = int(float(self.employment_rate) * 20)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Профиль: {self.teacher.full_name} ({self.get_academic_degree_display()})"

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
