from django.contrib import admin
from .models import TeacherProfile, CourseProfile, GroupProfile, AssignmentResult, ScheduleConflict

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'max_load_hours')
    filter_horizontal = ('specializations',)

@admin.register(CourseProfile)
class CourseProfileAdmin(admin.ModelAdmin):
    list_display = ('course', 'target_hours', 'course_type')
    list_filter = ('course_type',)

@admin.register(GroupProfile)
class GroupProfileAdmin(admin.ModelAdmin):
    list_display = ('group', 'student_count')

@admin.register(AssignmentResult)
class AssignmentResultAdmin(admin.ModelAdmin):
    list_display = ('course', 'teacher', 'is_confirmed', 'created_at')
    list_filter = ('is_confirmed',)

@admin.register(ScheduleConflict)
class ScheduleConflictAdmin(admin.ModelAdmin):
    list_display = ('severity', 'message', 'created_at')
    list_filter = ('severity',)
