from django import forms

from .models import (
    Building,
    CalendarEvent,
    ClassSession,
    ContactEntry,
    Course,
    Department,
    FaqEntry,
    IikoOutlet,
    MenuItem,
    NewsPost,
    Room,
    StudyGroup,
    StudyProgram,
    Teacher,
)


class DepartmentQuickForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'is_active', 'sort_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'ctl'}),
            'code': forms.TextInput(attrs={'class': 'ctl'}),
            'sort_order': forms.NumberInput(attrs={'class': 'ctl'}),
        }


class StudyProgramQuickForm(forms.ModelForm):
    class Meta:
        model = StudyProgram
        fields = ['name', 'code', 'level', 'is_active', 'sort_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'ctl'}),
            'code': forms.TextInput(attrs={'class': 'ctl'}),
            'sort_order': forms.NumberInput(attrs={'class': 'ctl'}),
        }


class StudyGroupQuickForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ['name', 'program', 'intake_year', 'is_active', 'sort_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'ctl'}),
            'program': forms.Select(attrs={'class': 'ctl'}),
            'intake_year': forms.NumberInput(attrs={'class': 'ctl'}),
            'sort_order': forms.NumberInput(attrs={'class': 'ctl'}),
        }


class TeacherQuickForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['full_name', 'department', 'position', 'email', 'phone', 'is_active']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'ctl', 'placeholder': 'ФИО полностью'}),
            'department': forms.Select(attrs={'class': 'ctl'}),
            'position': forms.TextInput(attrs={'class': 'ctl'}),
            'email': forms.EmailInput(attrs={'class': 'ctl'}),
            'phone': forms.TextInput(attrs={'class': 'ctl'}),
        }


class BuildingQuickForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ['name', 'code', 'address', 'is_active', 'sort_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'ctl'}),
            'code': forms.TextInput(attrs={'class': 'ctl'}),
            'address': forms.TextInput(attrs={'class': 'ctl'}),
            'sort_order': forms.NumberInput(attrs={'class': 'ctl'}),
        }


class RoomQuickForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['building', 'name', 'floor', 'capacity', 'is_active', 'sort_order']
        widgets = {
            'building': forms.Select(attrs={'class': 'ctl'}),
            'name': forms.TextInput(attrs={'class': 'ctl'}),
            'floor': forms.NumberInput(attrs={'class': 'ctl'}),
            'capacity': forms.NumberInput(attrs={'class': 'ctl'}),
            'sort_order': forms.NumberInput(attrs={'class': 'ctl'}),
        }


class CourseQuickForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'code', 'description', 'teacher', 'study_groups', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'ctl'}),
            'code': forms.TextInput(attrs={'class': 'ctl'}),
            'description': forms.Textarea(attrs={'class': 'ctl', 'rows': 3}),
            'teacher': forms.Select(attrs={'class': 'ctl'}),
            'study_groups': forms.SelectMultiple(
                attrs={'class': 'ctl', 'size': 8},
            ),
        }


class ClassSessionQuickForm(forms.ModelForm):
    class Meta:
        model = ClassSession
        fields = [
            'course',
            'title',
            'teacher',
            'starts_at',
            'ends_at',
            'room_ref',
            'room',
            'notes',
        ]
        widgets = {
            'course': forms.Select(attrs={'class': 'ctl'}),
            'teacher': forms.Select(attrs={'class': 'ctl'}),
            'title': forms.TextInput(attrs={'class': 'ctl', 'placeholder': 'Тема занятия'}),
            'starts_at': forms.DateTimeInput(
                attrs={'class': 'ctl', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'ends_at': forms.DateTimeInput(
                attrs={'class': 'ctl', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'room_ref': forms.Select(attrs={'class': 'ctl'}),
            'room': forms.TextInput(attrs={'class': 'ctl', 'placeholder': 'если нет в справочнике'}),
            'notes': forms.Textarea(attrs={'class': 'ctl', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['starts_at'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S']
        self.fields['ends_at'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S']


class CalendarEventQuickForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = [
            'title',
            'kind',
            'starts_on',
            'ends_on',
            'description',
            'is_published',
            'sort_order',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'ctl'}),
            'kind': forms.Select(attrs={'class': 'ctl'}),
            'starts_on': forms.DateInput(attrs={'class': 'ctl', 'type': 'date'}),
            'ends_on': forms.DateInput(attrs={'class': 'ctl', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'ctl', 'rows': 3}),
            'sort_order': forms.NumberInput(attrs={'class': 'ctl'}),
        }


class NewsPostQuickForm(forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = [
            'title',
            'slug',
            'summary',
            'body',
            'published_at',
            'is_published',
            'is_pinned',
            'sort_order',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'ctl'}),
            'slug': forms.TextInput(attrs={'class': 'ctl'}),
            'summary': forms.TextInput(attrs={'class': 'ctl'}),
            'body': forms.Textarea(attrs={'class': 'ctl', 'rows': 5}),
            'published_at': forms.DateTimeInput(
                attrs={'class': 'ctl', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'sort_order': forms.NumberInput(attrs={'class': 'ctl'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['published_at'].required = False
        self.fields['published_at'].input_formats = [
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%d %H:%M:%S',
        ]


class ContactEntryQuickForm(forms.ModelForm):
    class Meta:
        model = ContactEntry
        fields = [
            'title',
            'role_hint',
            'phone',
            'email',
            'address',
            'office_hours',
            'notes',
            'is_active',
            'sort_order',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'ctl'}),
            'role_hint': forms.TextInput(attrs={'class': 'ctl'}),
            'phone': forms.TextInput(attrs={'class': 'ctl'}),
            'email': forms.EmailInput(attrs={'class': 'ctl'}),
            'address': forms.TextInput(attrs={'class': 'ctl'}),
            'office_hours': forms.TextInput(attrs={'class': 'ctl'}),
            'notes': forms.Textarea(attrs={'class': 'ctl', 'rows': 2}),
            'sort_order': forms.NumberInput(attrs={'class': 'ctl'}),
        }


class FaqQuickForm(forms.ModelForm):
    class Meta:
        model = FaqEntry
        fields = ['question', 'answer', 'keywords', 'sort_order', 'is_active']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'ctl'}),
            'answer': forms.Textarea(attrs={'class': 'ctl', 'rows': 4}),
            'keywords': forms.TextInput(attrs={'class': 'ctl', 'placeholder': 'через запятую'}),
        }


class IikoOutletQuickForm(forms.ModelForm):
    class Meta:
        model = IikoOutlet
        fields = ['name', 'address', 'phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'ctl'}),
            'address': forms.TextInput(attrs={'class': 'ctl'}),
            'phone': forms.TextInput(attrs={'class': 'ctl'}),
        }


class MenuItemQuickForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['outlet', 'name', 'category', 'price', 'is_available', 'sort_order']
        widgets = {
            'outlet': forms.Select(attrs={'class': 'ctl'}),
            'name': forms.TextInput(attrs={'class': 'ctl'}),
            'category': forms.TextInput(attrs={'class': 'ctl'}),
            'price': forms.NumberInput(attrs={'class': 'ctl', 'step': '0.01'}),
        }
