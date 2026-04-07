from django.urls import path
from . import views

urlpatterns = [
    path('load-dashboard/', views.load_dashboard, name='load-dashboard'),
    path('run-distributor/', views.run_distributor, name='run-distributor'),
    path('schedule-dashboard/', views.schedule_dashboard, name='schedule-dashboard'),
    path('run-scheduler/', views.run_scheduler, name='run-scheduler'),
    path('clear-all/', views.clear_all, name='clear-all'),
    path('teacher/<int:teacher_id>/', views.teacher_detail, name='teacher-detail'),
    path('teacher/<int:teacher_id>/assign/', views.manual_assign_course, name='manual-assign-course'),
    path('assignment/<int:assignment_id>/remove/', views.remove_assignment, name='remove-assignment'),
    path('run-setup-expert/', views.run_setup_expert, name='run-setup-expert'),
    path('create-teacher-manual/', views.create_teacher_manual, name='create-teacher-manual'),
    path('create-course-manual/', views.create_course_manual, name='create-course-manual'),
    path('run-system-initializer/', views.run_system_initializer, name='run-system-initializer'),
    path('teacher/<int:teacher_id>/edit/', views.edit_teacher_manual, name='edit-teacher-manual'),
    path('teacher/<int:teacher_id>/delete/', views.delete_teacher, name='delete-teacher'),
]
