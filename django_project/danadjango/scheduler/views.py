from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from metapko.models import Teacher, Course, StudyGroup, Room, ClassSession
from .models import TeacherProfile, CourseProfile, GroupProfile, AssignmentResult, ScheduleConflict
from .logic.distributor import LoadDistributor
from .logic.scheduler import ScheduleGenerator
from .forms import ManualAssignForm

@login_required
def load_dashboard(request):
    """Панель управления нагрузкой."""
    teachers = Teacher.objects.filter(is_active=True).prefetch_related('scheduler_profile')
    for teacher in teachers:
        # Обеспечиваем наличие профиля
        if not hasattr(teacher, 'scheduler_profile'):
            TeacherProfile.objects.get_or_create(teacher=teacher)
            
    courses = Course.objects.filter(is_active=True).prefetch_related('scheduler_profile')
    for course in courses:
        if not hasattr(course, 'scheduler_profile'):
            CourseProfile.objects.get_or_create(course=course)

    assignments = AssignmentResult.objects.all()
    conflicts = ScheduleConflict.objects.all()

    context = {
        'teachers': teachers,
        'courses': courses,
        'assignments': assignments,
        'conflicts': conflicts,
        'portal_title': 'Планирование нагрузки',
    }
    return render(request, 'scheduler/load_dashboard.html', context)

@login_required
def run_distributor(request):
    """Запуск алгоритма распределения нагрузки."""
    distributor = LoadDistributor()
    distributor.distribute()
    messages.success(request, 'Алгоритм распределения нагрузки выполнен.')
    return redirect('load-dashboard')

@login_required
def schedule_dashboard(request):
    """Панель управления расписанием."""
    sessions = ClassSession.objects.all().order_by('starts_at')
    
    # Фильтрация
    teacher_id = request.GET.get('teacher_id')
    group_id = request.GET.get('group_id')
    room_id = request.GET.get('room_id')

    if teacher_id:
        sessions = sessions.filter(teacher_id=teacher_id)
    if group_id:
        sessions = sessions.filter(course__study_groups__id=group_id)
    if room_id:
        sessions = sessions.filter(room_ref_id=room_id)

    conflicts = ScheduleConflict.objects.all()
    
    # Списки для селекторов фильтра
    teachers = Teacher.objects.filter(is_active=True)
    groups = StudyGroup.objects.filter(is_active=True)
    rooms = Room.objects.filter(is_active=True)
    
    context = {
        'sessions': sessions,
        'conflicts': conflicts,
        'teachers': teachers,
        'groups': groups,
        'rooms': rooms,
        'current_teacher_id': teacher_id,
        'current_group_id': group_id,
        'current_room_id': room_id,
        'portal_title': 'Генератор расписания',
    }
    return render(request, 'scheduler/schedule_dashboard.html', context)

@login_required
def run_scheduler(request):
    """Запуск генератора расписания."""
    generator = ScheduleGenerator()
    generator.generate()
    messages.success(request, 'Расписание успешно сгенерировано.')
    return redirect('schedule-dashboard')

@login_required
def clear_all(request):
    """Сброс всех данных планирования."""
    AssignmentResult.objects.all().delete()
    ClassSession.objects.filter(starts_at__year__gte=2024).delete()
    ScheduleConflict.objects.all().delete()
    messages.warning(request, 'Все данные планирования очищены.')
    return redirect('load-dashboard')

from django.shortcuts import get_object_or_404
from django.db.models import Sum

@login_required
def teacher_detail(request, teacher_id):
    """Карточка преподавателя."""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    # Обеспечиваем наличие профиля
    profile, _ = TeacherProfile.objects.get_or_create(teacher=teacher)
    
    assignments = AssignmentResult.objects.filter(teacher=teacher)
    
    # Считаем текущую нагрузку из буфера
    current_load = assignments.aggregate(
        total=Sum('course__scheduler_profile__target_hours')
    )['total'] or 0
    
    # Свободные курсы для ручного назначения
    assigned_course_ids = AssignmentResult.objects.values_list('course_id', flat=True)
    unassigned_courses = Course.objects.exclude(id__in=assigned_course_ids)
    
    context = {
        't': teacher,
        'profile': profile,
        'assignments': assignments,
        'current_load': current_load,
        'unassigned_courses': unassigned_courses,
        'portal_title': f'Преподаватель: {teacher.full_name}',
    }
    return render(request, 'scheduler/teacher_detail.html', context)

@login_required
def manual_assign_course(request, teacher_id):
    """Ручное назначение курса преподавателю."""
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        if course_id:
            course = get_object_or_404(Course, id=course_id)
            teacher = get_object_or_404(Teacher, id=teacher_id)
            AssignmentResult.objects.create(course=course, teacher=teacher, is_confirmed=True)
            messages.success(request, f'Курс "{course.title}" успешно назначен {teacher.full_name}.')
    return redirect('teacher-detail', teacher_id=teacher_id)

from .logic.setup_expert import SetupExpert

@login_required
def run_setup_expert(request):
    """Запуск эксперта по подготовке данных."""
    stats = SetupExpert.fill_missing_profiles()
    messages.success(request, f'Эксперт завершил работу. Создано профилей: Учителя ({stats["teachers"]}), Курсы ({stats["courses"]}), Группы ({stats["groups"]}).')
    return redirect('load-dashboard')

@login_required
def create_teacher_manual(request):
    """Ручное создание преподавателя и его профиля."""
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        position = request.POST.get('position', '')
        degree = request.POST.get('degree', 'none')
        rate = request.POST.get('rate', '1.0')
        
        if full_name:
            # Создаем базового преподавателя в metapko
            teacher = Teacher.objects.create(
                full_name=full_name,
                position=position,
                is_active=True
            )
            # Создаем его профиль в scheduler
            TeacherProfile.objects.create(
                teacher=teacher,
                academic_degree=degree,
                employment_rate=float(rate)
            )
            messages.success(request, f'Преподаватель {full_name} успешно добавлен.')
        else:
            messages.error(request, 'ФИО обязательно для заполнения.')
            
    return redirect('load-dashboard')

@login_required
def remove_assignment(request, assignment_id):
    """Снятие дисциплины с преподавателя."""
    assignment = get_object_or_404(AssignmentResult, id=assignment_id)
    t_id = assignment.teacher.id
    assignment.delete()
    messages.warning(request, 'Назначение снято.')
    return redirect('teacher-detail', teacher_id=t_id)
