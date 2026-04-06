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
]
