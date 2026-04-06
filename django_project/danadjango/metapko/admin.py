from django.contrib import admin
from django.contrib import messages

from .admin_site import meta_pko_admin
from .models import (
    Building,
    CalendarEvent,
    ClassSession,
    ContactEntry,
    Course,
    CustomerOrder,
    Department,
    FaqEntry,
    IntegrationClient,
    IikoOutlet,
    MenuItem,
    NewsPost,
    OrderLine,
    Room,
    ServiceTicket,
    StudyGroup,
    StudyProgram,
    Teacher,
)


@admin.register(IntegrationClient, site=meta_pko_admin)
class IntegrationClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'last_used_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'notes')
    readonly_fields = ('key_hash', 'created_at', 'last_used_at')

    def save_model(self, request, obj, form, change):
        if not change:
            raw = IntegrationClient.generate_raw_key()
            obj.set_key(raw)
            super().save_model(request, obj, form, change)
            self.message_user(
                request,
                f'Сохраните API-ключ (больше не показывается): {raw}',
                level=messages.WARNING,
            )
        else:
            super().save_model(request, obj, form, change)


@admin.register(Department, site=meta_pko_admin)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(Teacher, site=meta_pko_admin)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'department', 'position', 'email', 'is_active')
    list_filter = ('is_active', 'department')
    search_fields = ('full_name', 'email', 'phone', 'position')


@admin.register(StudyProgram, site=meta_pko_admin)
class StudyProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'level', 'is_active', 'sort_order')
    list_filter = ('level', 'is_active')
    search_fields = ('name', 'code')


@admin.register(StudyGroup, site=meta_pko_admin)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'program', 'intake_year', 'is_active', 'sort_order')
    list_filter = ('program', 'is_active')
    search_fields = ('name',)


@admin.register(Building, site=meta_pko_admin)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'address', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'address')


@admin.register(Room, site=meta_pko_admin)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'building', 'floor', 'capacity', 'is_active')
    list_filter = ('building', 'is_active')
    search_fields = ('name', 'building__name')


@admin.register(Course, site=meta_pko_admin)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'teacher', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'code', 'description')
    filter_horizontal = ('study_groups',)


@admin.register(ClassSession, site=meta_pko_admin)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'teacher', 'starts_at', 'ends_at', 'room_ref', 'room')
    list_filter = ('course', 'teacher', 'room_ref__building')
    search_fields = ('title', 'room', 'notes')
    autocomplete_fields = ('room_ref',)
    date_hierarchy = 'starts_at'


@admin.register(FaqEntry, site=meta_pko_admin)
class FaqEntryAdmin(admin.ModelAdmin):
    list_display = ('question', 'sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer', 'keywords')


@admin.register(CalendarEvent, site=meta_pko_admin)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'starts_on', 'ends_on', 'is_published')
    list_filter = ('kind', 'is_published')
    search_fields = ('title', 'description')
    date_hierarchy = 'starts_on'


@admin.register(NewsPost, site=meta_pko_admin)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'is_pinned', 'published_at', 'sort_order')
    list_filter = ('is_published', 'is_pinned')
    search_fields = ('title', 'summary', 'body')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'


@admin.register(ContactEntry, site=meta_pko_admin)
class ContactEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'role_hint', 'phone', 'email', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('title', 'role_hint', 'phone', 'email', 'address')


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0


@admin.register(IikoOutlet, site=meta_pko_admin)
class IikoOutletAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')


@admin.register(MenuItem, site=meta_pko_admin)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'outlet', 'category', 'price', 'is_available', 'sort_order')
    list_filter = ('is_available', 'outlet', 'category')
    search_fields = ('name', 'category')


@admin.register(CustomerOrder, site=meta_pko_admin)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'outlet', 'status', 'customer_name', 'phone', 'created_at')
    list_filter = ('status', 'outlet')
    search_fields = ('customer_name', 'phone', 'notes', 'external_ref')
    inlines = [OrderLineInline]
    date_hierarchy = 'created_at'


@admin.register(ServiceTicket, site=meta_pko_admin)
class ServiceTicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'outlet', 'status', 'priority', 'requester_name', 'created_at')
    list_filter = ('status', 'priority', 'outlet')
    search_fields = ('title', 'description', 'requester_name', 'contact')
