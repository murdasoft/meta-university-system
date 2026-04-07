from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from metapko.models import Teacher, Course, StudyGroup, Room, Building, ClassSession
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
    """Полная очистка системы (RESET)."""
    # Удаляем всё по цепочке, чтобы начать с нуля
    ClassSession.objects.all().delete()
    AssignmentResult.objects.all().delete()
    Course.objects.all().delete()
    StudyGroup.objects.all().delete() # По ТЗ это группы
    Room.objects.all().delete()
    Building.objects.all().delete()
    Teacher.objects.all().delete()
    TeacherProfile.objects.all().delete()
    
    messages.warning(request, "Система полностью очищена. Теперь вы можете запустить быстрый старт или ввести данные вручную.")
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
def create_course_manual(request):
    """Ручное создание дисциплины и её профиля."""
    from metapko.models import StudyGroup
    
    if request.method == 'POST':
        title = request.POST.get('title')
        hours = request.POST.get('hours', '32')
        course_type = request.POST.get('type', 'lecture')
        
        if title:
            # Создаем базовый курс в metapko
            course = Course.objects.create(title=title, code=title[:10].upper())
            
            # Привязываем ко всем группам по умолчанию для теста (или к первой встречной)
            groups = StudyGroup.objects.all()
            if groups.exists():
                course.study_groups.set(groups)
                
            # Создаем его профиль в scheduler
            CourseProfile.objects.create(
                course=course,
                target_hours=int(hours),
                course_type=course_type
            )
            messages.success(request, f'Дисциплина "{title}" успешно создана.')
        else:
            messages.error(request, 'Название обязательно.')
            
    return redirect('load-dashboard')

@login_required
def assign_teacher_from_dashboard(request):
    """Быстрая привязка преподавателя к дисциплине из общей таблицы."""
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        teacher_id = request.POST.get('teacher_id')
        
        if course_id and teacher_id:
            course = get_object_or_404(Course, id=course_id)
            teacher = get_object_or_404(Teacher, id=teacher_id)
            
            # 1. Обновляем основную модель (metapko)
            course.teacher = teacher
            course.save()
            
            # 2. Синхронизируем с результатами планировщика (scheduler)
            AssignmentResult.objects.filter(course=course).delete()
            AssignmentResult.objects.create(
                course=course,
                teacher=teacher,
                is_confirmed=True
            )
            messages.success(request, f'Дисциплина "{course.title}" успешно закреплена за {teacher.full_name}.')
        else:
            messages.error(request, 'Ошибка привязки: не выбраны данные.')
            
    return redirect('load-dashboard')

from .logic.initializer import SystemInitializer

@login_required
def run_system_initializer(request):
    """Наполнение системы демонстрационными данными."""
    stats = SystemInitializer.run_seed()
    messages.success(request, f'Система инициализирована. Добавлено: Аудитории ({stats["rooms"]}), Группы ({stats["groups"]}), Курсы ({stats["courses"]}).')
    return redirect('load-dashboard')

@login_required
def edit_teacher_manual(request, teacher_id):
    """Редактирование ФИО и параметров преподавателя."""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    profile, _ = TeacherProfile.objects.get_or_create(teacher=teacher)
    
    if request.method == 'POST':
        teacher.full_name = request.POST.get('full_name', teacher.full_name)
        teacher.position = request.POST.get('position', teacher.position)
        teacher.save()
        
        profile.academic_degree = request.POST.get('degree', profile.academic_degree)
        profile.employment_rate = float(request.POST.get('rate', profile.employment_rate))
        profile.save()
        
        messages.success(request, f'Данные преподавателя {teacher.full_name} обновлены.')
        
    return redirect('load-dashboard')

@login_required
def delete_teacher(request, teacher_id):
    """Удаление преподавателя."""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    name = teacher.full_name
    teacher.delete()
    messages.warning(request, f'Преподаватель {name} удален из системы.')
    return redirect('load-dashboard')

@login_required
def remove_assignment(request, assignment_id):
    """Снятие дисциплины с преподавателя."""
    assignment = get_object_or_404(AssignmentResult, id=assignment_id)
    t_id = assignment.teacher.id
    assignment.delete()
    messages.warning(request, 'Назначение снято.')
    return redirect('teacher-detail', teacher_id=t_id)
