from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin

from .forms import (
    BuildingQuickForm,
    CalendarEventQuickForm,
    ClassSessionQuickForm,
    ContactEntryQuickForm,
    CourseQuickForm,
    DepartmentQuickForm,
    FaqQuickForm,
    IikoOutletQuickForm,
    MenuItemQuickForm,
    NewsPostQuickForm,
    RoomQuickForm,
    StudyGroupQuickForm,
    StudyProgramQuickForm,
    TeacherQuickForm,
)

from .models import (
    Building,
    CalendarEvent,
    ClassSession,
    ContactEntry,
    Course,
    CustomerOrder,
    FaqEntry,
    IntegrationClient,
    IikoOutlet,
    MenuItem,
    NewsPost,
    Room,
    ServiceTicket,
    StudyGroup,
    StudyProgram,
    Teacher,
)


def metapko_portal_index(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('metapko-dashboard')
    return redirect('metapko-login')


class StaffPortalRequiredMixin(UserPassesTestMixin):
    """Доступ к порталу только у staff (те же учётки, что для meta-admin)."""

    login_url = reverse_lazy('metapko-login')

    def test_func(self):
        u = self.request.user
        return u.is_authenticated and u.is_staff


class MetaPkoLoginView(LoginView):
    template_name = 'metapko/login.dj.html'
    redirect_authenticated_user = False

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('metapko-dashboard')
            messages.info(
                request,
                'Портал доступен только сотрудникам (staff). Вы вошли как обычный пользователь.',
            )
            return redirect('/login/')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('metapko-dashboard')

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_staff:
            messages.error(
                self.request,
                'Вход разрешён только сотрудникам (галочка «Статус персонала» в учётной записи).',
            )
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['portal_hint_login'] = getattr(settings, 'METAPKO_PORTAL_HINT_LOGIN', '') or ''
        ctx['portal_hint_password'] = getattr(settings, 'METAPKO_PORTAL_HINT_PASSWORD', '') or ''
        return ctx


class MetaPkoLogoutView(LogoutView):
    next_page = reverse_lazy('metapko-login')


class MetaPkoDashboardView(StaffPortalRequiredMixin, TemplateView):
    template_name = 'metapko/dashboard.dj.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['portal_title'] = 'IIKO · Meta-университет'
        ctx['portal_tagline'] = (
            'Управление безопасным API-доступом к IIKO для интеграции с внешними сервисами '
            'Meta-университета и Telegram-ботом.'
        )
        ctx['metapko_enabled'] = getattr(settings, 'METAPKO_ENABLED', True)
        ctx['api_key_header'] = getattr(settings, 'METAPKO_API_KEY_HEADER', 'X-Meta-PKO-Key')

        qs = IntegrationClient.objects.all()
        ctx['clients_total'] = qs.count()
        ctx['clients_active'] = qs.filter(is_active=True).count()
        last = qs.order_by('-last_used_at').first()
        ctx['last_client_used'] = last
        recent = qs.order_by('-created_at')[:5]
        ctx['recent_clients'] = list(recent)

        ctx['stat_teachers'] = Teacher.objects.filter(is_active=True).count()
        ctx['stat_courses'] = Course.objects.filter(is_active=True).count()
        ctx['stat_sessions'] = ClassSession.objects.count()
        ctx['stat_faq'] = FaqEntry.objects.filter(is_active=True).count()
        ctx['stat_outlets'] = IikoOutlet.objects.filter(is_active=True).count()
        ctx['stat_menu'] = MenuItem.objects.filter(is_available=True).count()
        ctx['stat_orders'] = CustomerOrder.objects.count()
        ctx['stat_tickets'] = ServiceTicket.objects.exclude(
            status=ServiceTicket.Status.DONE,
        ).exclude(status=ServiceTicket.Status.CANCELLED).count()

        ctx['stat_programs'] = StudyProgram.objects.filter(is_active=True).count()
        ctx['stat_groups'] = StudyGroup.objects.filter(is_active=True).count()
        ctx['stat_buildings'] = Building.objects.filter(is_active=True).count()
        ctx['stat_rooms'] = Room.objects.filter(is_active=True).count()
        ctx['stat_calendar'] = CalendarEvent.objects.filter(is_published=True).count()
        ctx['stat_news'] = NewsPost.objects.filter(is_published=True).count()
        ctx['stat_contacts'] = ContactEntry.objects.filter(is_active=True).count()

        return ctx


class _QuickAddMixin(StaffPortalRequiredMixin):
    template_name = 'metapko/quick_form.dj.html'
    success_url = reverse_lazy('metapko-dashboard')
    form_title = 'Добавить запись'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['portal_title'] = 'IIKO · Meta-университет'
        ctx['form_title'] = self.form_title
        return ctx

    def form_valid(self, form):
        messages.success(self.request, self.done_message)
        return super().form_valid(form)


class QuickAddDepartmentView(_QuickAddMixin, CreateView):
    form_class = DepartmentQuickForm
    form_title = 'Кафедра'
    done_message = 'Кафедра сохранена — данные доступны в API и боте.'


class QuickAddTeacherView(_QuickAddMixin, CreateView):
    form_class = TeacherQuickForm
    form_title = 'Преподаватель'
    done_message = 'Преподаватель добавлен — смотрите /teachers в боте.'


class QuickAddCourseView(_QuickAddMixin, CreateView):
    form_class = CourseQuickForm
    form_title = 'Курс'
    done_message = 'Курс добавлен.'


class QuickAddClassSessionView(_QuickAddMixin, CreateView):
    form_class = ClassSessionQuickForm
    form_title = 'Занятие'
    done_message = 'Занятие добавлено — смотрите /sessions в боте.'


class QuickAddFaqView(_QuickAddMixin, CreateView):
    form_class = FaqQuickForm
    form_title = 'FAQ'
    done_message = 'FAQ сохранён — смотрите /faq в боте.'


class QuickAddOutletView(_QuickAddMixin, CreateView):
    form_class = IikoOutletQuickForm
    form_title = 'Точка IIKO'
    done_message = 'Точка добавлена.'


class QuickAddMenuItemView(_QuickAddMixin, CreateView):
    form_class = MenuItemQuickForm
    form_title = 'Позиция меню'
    done_message = 'Позиция меню добавлена.'


class QuickAddStudyProgramView(_QuickAddMixin, CreateView):
    form_class = StudyProgramQuickForm
    form_title = 'Учебная программа'
    done_message = 'Программа сохранена. API: /api/metapko/v1/study-programs/'


class QuickAddStudyGroupView(_QuickAddMixin, CreateView):
    form_class = StudyGroupQuickForm
    form_title = 'Учебная группа'
    done_message = 'Группа сохранена. API: /api/metapko/v1/study-groups/'


class QuickAddBuildingView(_QuickAddMixin, CreateView):
    form_class = BuildingQuickForm
    form_title = 'Корпус'
    done_message = 'Корпус добавлен. API: /api/metapko/v1/buildings/'


class QuickAddRoomView(_QuickAddMixin, CreateView):
    form_class = RoomQuickForm
    form_title = 'Аудитория'
    done_message = 'Аудитория добавлена. API: /api/metapko/v1/rooms/'


class QuickAddCalendarEventView(_QuickAddMixin, CreateView):
    form_class = CalendarEventQuickForm
    form_title = 'Событие календаря'
    done_message = 'Событие сохранено. API: /api/metapko/v1/calendar/ (в боте: /calendar).'


class QuickAddNewsPostView(_QuickAddMixin, CreateView):
    form_class = NewsPostQuickForm
    form_title = 'Новость / объявление'
    done_message = 'Публикация сохранена. API: /api/metapko/v1/news/ (в боте: /news).'


class QuickAddContactEntryView(_QuickAddMixin, CreateView):
    form_class = ContactEntryQuickForm
    form_title = 'Контакт справочника'
    done_message = 'Контакт сохранён. API: /api/metapko/v1/contacts/ (в боте: /contacts).'
