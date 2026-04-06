from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HealthView, ProtectedInfoView
from .views_api import (
    BuildingViewSet,
    CalendarEventViewSet,
    ClassSessionViewSet,
    ContactEntryViewSet,
    CourseViewSet,
    CustomerOrderViewSet,
    DepartmentViewSet,
    FaqViewSet,
    IikoOutletViewSet,
    MenuItemViewSet,
    NewsPostViewSet,
    RoomViewSet,
    ServiceTicketViewSet,
    StudyGroupViewSet,
    StudyProgramViewSet,
    TeacherViewSet,
)

router = DefaultRouter()
router.register(r'v1/departments', DepartmentViewSet, basename='metapko-departments')
router.register(r'v1/teachers', TeacherViewSet, basename='metapko-teachers')
router.register(r'v1/study-programs', StudyProgramViewSet, basename='metapko-study-programs')
router.register(r'v1/study-groups', StudyGroupViewSet, basename='metapko-study-groups')
router.register(r'v1/courses', CourseViewSet, basename='metapko-courses')
router.register(r'v1/class-sessions', ClassSessionViewSet, basename='metapko-class-sessions')
router.register(r'v1/faq', FaqViewSet, basename='metapko-faq')
router.register(r'v1/buildings', BuildingViewSet, basename='metapko-buildings')
router.register(r'v1/rooms', RoomViewSet, basename='metapko-rooms')
router.register(r'v1/calendar', CalendarEventViewSet, basename='metapko-calendar')
router.register(r'v1/news', NewsPostViewSet, basename='metapko-news')
router.register(r'v1/contacts', ContactEntryViewSet, basename='metapko-contacts')
router.register(r'v1/outlets', IikoOutletViewSet, basename='metapko-outlets')
router.register(r'v1/menu-items', MenuItemViewSet, basename='metapko-menu-items')
router.register(r'v1/orders', CustomerOrderViewSet, basename='metapko-orders')
router.register(r'v1/service-tickets', ServiceTicketViewSet, basename='metapko-service-tickets')

urlpatterns = [
    path('v1/health/', HealthView.as_view(), name='metapko-health'),
    path('v1/me/', ProtectedInfoView.as_view(), name='metapko-me'),
    path('', include(router.urls)),
]
