from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.exceptions import ValidationError

from .authentication import IntegrationApiKeyAuthentication
from .models import (
    Building,
    CalendarEvent,
    ClassSession,
    ContactEntry,
    Course,
    CustomerOrder,
    Department,
    FaqEntry,
    IikoOutlet,
    MenuItem,
    NewsPost,
    Room,
    ServiceTicket,
    StudyGroup,
    StudyProgram,
    Teacher,
)
from .permissions import HasIntegrationClient
from .serializers import (
    BuildingSerializer,
    CalendarEventSerializer,
    ClassSessionSerializer,
    ContactEntrySerializer,
    CourseSerializer,
    CustomerOrderCreateSerializer,
    CustomerOrderSerializer,
    DepartmentSerializer,
    FaqEntrySerializer,
    IikoOutletSerializer,
    MenuItemSerializer,
    NewsPostSerializer,
    RoomSerializer,
    ServiceTicketSerializer,
    StudyGroupSerializer,
    StudyProgramSerializer,
    TeacherSerializer,
)


class PartnerViewSet(viewsets.GenericViewSet):
    """Доступ только по API-ключу клиента интеграции."""

    authentication_classes = [IntegrationApiKeyAuthentication]
    permission_classes = [HasIntegrationClient]


class DepartmentViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['sort_order', 'name']


class TeacherViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = Teacher.objects.filter(is_active=True).select_related('department')
    serializer_class = TeacherSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'is_active']
    search_fields = ['full_name', 'email', 'position']
    ordering_fields = ['full_name']


class CourseViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = (
        Course.objects.filter(is_active=True)
        .select_related('teacher')
        .prefetch_related('study_groups__program')
    )
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['teacher', 'is_active', 'study_groups']
    search_fields = ['title', 'code', 'description']
    ordering_fields = ['title']


class ClassSessionViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = ClassSession.objects.select_related(
        'course',
        'teacher',
        'room_ref',
        'room_ref__building',
    ).all()
    serializer_class = ClassSessionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'teacher', 'room_ref']
    ordering_fields = ['starts_at', 'ends_at']

    def get_queryset(self):
        qs = super().get_queryset()
        df = self.request.query_params.get('from_date')
        dt = self.request.query_params.get('to_date')
        if df:
            start = parse_datetime(df)
            if start is None:
                raise ValidationError({'from_date': 'Некорректная дата (ISO-8601)'})
            if timezone.is_naive(start):
                start = timezone.make_aware(start, timezone.get_current_timezone())
            qs = qs.filter(starts_at__gte=start)
        if dt:
            end = parse_datetime(dt)
            if end is None:
                raise ValidationError({'to_date': 'Некорректная дата (ISO-8601)'})
            if timezone.is_naive(end):
                end = timezone.make_aware(end, timezone.get_current_timezone())
            qs = qs.filter(starts_at__lte=end)
        return qs


class FaqViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = FaqEntry.objects.filter(is_active=True)
    serializer_class = FaqEntrySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['question', 'answer', 'keywords']
    ordering_fields = ['sort_order', 'id']


class StudyProgramViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = StudyProgram.objects.filter(is_active=True)
    serializer_class = StudyProgramSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['sort_order', 'name']


class StudyGroupViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = StudyGroup.objects.filter(is_active=True).select_related('program')
    serializer_class = StudyGroupSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['program', 'intake_year', 'is_active']
    search_fields = ['name']
    ordering_fields = ['sort_order', 'name']


class BuildingViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = Building.objects.filter(is_active=True)
    serializer_class = BuildingSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'address']
    ordering_fields = ['sort_order', 'name']


class RoomViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = Room.objects.filter(is_active=True).select_related('building').order_by(
        'building',
        'sort_order',
        'name',
    )
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['building', 'floor', 'is_active']
    search_fields = ['name', 'building__name', 'building__code']
    ordering_fields = ['sort_order', 'name', 'building']


class CalendarEventViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = CalendarEvent.objects.filter(is_published=True)
    serializer_class = CalendarEventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['kind']
    search_fields = ['title', 'description']
    ordering_fields = ['starts_on', 'sort_order', 'id']

    def get_queryset(self):
        qs = super().get_queryset()
        df = self.request.query_params.get('from_date')
        dt = self.request.query_params.get('to_date')
        if df:
            d = parse_date(df)
            if d:
                qs = qs.filter(starts_on__gte=d)
        if dt:
            d = parse_date(dt)
            if d:
                qs = qs.filter(starts_on__lte=d)
        return qs


class NewsPostViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = NewsPost.objects.filter(is_published=True).order_by(
        '-is_pinned',
        '-published_at',
        'sort_order',
    )
    serializer_class = NewsPostSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'summary', 'body']
    ordering_fields = ['published_at', 'sort_order', 'id', 'is_pinned']


class ContactEntryViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = ContactEntry.objects.filter(is_active=True)
    serializer_class = ContactEntrySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'role_hint', 'phone', 'email', 'address', 'notes']
    ordering_fields = ['sort_order', 'title']


class IikoOutletViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = IikoOutlet.objects.filter(is_active=True)
    serializer_class = IikoOutletSerializer


class MenuItemViewSet(PartnerViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = MenuItem.objects.select_related('outlet').all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['outlet', 'is_available', 'category']
    search_fields = ['name', 'category']
    ordering_fields = ['sort_order', 'name', 'price']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('available_only', '').lower() in ('1', 'true', 'yes'):
            qs = qs.filter(is_available=True)
        return qs


class CustomerOrderViewSet(PartnerViewSet, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CustomerOrder.objects.prefetch_related('lines').all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['outlet', 'status']
    ordering_fields = ['created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomerOrderCreateSerializer
        return CustomerOrderSerializer


class ServiceTicketViewSet(
    PartnerViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ServiceTicket.objects.all()
    serializer_class = ServiceTicketSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['outlet', 'status', 'priority']
    ordering_fields = ['created_at']
