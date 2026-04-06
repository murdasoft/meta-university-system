from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    # AI чат
    path('chat/', views.chat_view, name='chat'),
    path('quick-action/', views.quick_action_view, name='quick-action'),
    
    # История чата
    path('history/', views.chat_history_view, name='history'),
    path('session/<uuid:session_id>/', views.chat_session_view, name='session'),
    path('session/<uuid:session_id>/delete/', views.delete_chat_session_view, name='delete-session'),
    
    # Квота
    path('quota/', views.ai_quota_view, name='quota'),
]
