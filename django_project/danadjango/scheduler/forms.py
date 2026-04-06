from django import forms
from metapko.models import Course, Teacher, Room, StudyGroup
from .models import AssignmentResult
from datetime import datetime, time

class ManualAssignForm(forms.ModelForm):
    class Meta:
        model = AssignmentResult
        fields = ['course', 'teacher']

class ManualSessionForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label="Дисциплина")
    teacher = forms.ModelChoiceField(queryset=Teacher.objects.filter(is_active=True), label="Преподаватель")
    room_ref = forms.ModelChoiceField(queryset=Room.objects.filter(is_active=True), label="Аудитория")
    day_offset = forms.IntegerField(label="День недели (0=Пн, 4=Пт)", min_value=0, max_value=4)
    slot_index = forms.IntegerField(label="Номер пары (0-3)", min_value=0, max_value=3)
