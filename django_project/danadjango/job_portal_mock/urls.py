from django.urls import path

from . import views

app_name = 'job_portal_mock'

urlpatterns = [
    path('', views.home, name='home'),
    path('vacancies/', views.vacancies_list, name='vacancies'),
    path('vacancies/<slug:slug>/', views.vacancy_detail, name='vacancy_detail'),
    path('login/', views.mock_login, name='login'),
    path('register/', views.mock_register, name='register'),
    path('logout/', views.mock_logout, name='mock_logout'),
    # Соискатель
    path('seeker/', views.seeker_dashboard, name='seeker_dashboard'),
    path('seeker/resumes/', views.seeker_resumes, name='seeker_resumes'),
    path('seeker/applications/', views.seeker_applications, name='seeker_applications'),
    path('seeker/saved/', views.seeker_saved, name='seeker_saved'),
    path('seeker/settings/', views.seeker_settings, name='seeker_settings'),
    path('seeker/notifications/', views.seeker_notifications, name='seeker_notifications'),
    # Работодатель
    path('employer/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/vacancies/', views.employer_vacancies, name='employer_vacancies'),
    path('employer/applications/', views.employer_applications, name='employer_applications'),
    path('employer/resume-search/', views.employer_resume_search, name='employer_resume_search'),
    path('employer/company/', views.employer_company, name='employer_company'),
    path('employer/notifications/', views.employer_notifications, name='employer_notifications'),
    # Админ-панель (макет)
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/moderation/', views.admin_moderation, name='admin_moderation'),
    path('admin-panel/directories/', views.admin_directories, name='admin_directories'),
    path('admin-panel/reports/', views.admin_reports, name='admin_reports'),
    path('admin-panel/system/', views.admin_system, name='admin_system'),
]
