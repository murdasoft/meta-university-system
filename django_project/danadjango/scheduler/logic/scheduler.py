from datetime import datetime, timedelta, time
from django.utils import timezone
from metapko.models import Teacher, Course, StudyGroup, Room, ClassSession
from scheduler.models import TeacherProfile, CourseProfile, GroupProfile, AssignmentResult, ScheduleConflict

class ScheduleGenerator:
    def __init__(self, start_date=None):
        if not start_date:
            today = timezone.now().date()
            # Находим ближайший понедельник (weekday() возвращает 0 для Пн)
            self.start_date = today - timedelta(days=today.weekday())
        else:
            self.start_date = start_date
        self.slots = [
            (time(8, 30), time(10, 0)),
            (time(10, 15), time(11, 45)),
            (time(12, 30), time(14, 0)),
            (time(14, 15), time(15, 45)),
        ]
        self.days_to_plan = 5 # Пн-Пт

    def generate(self):
        """
        Генерация расписания на основе распределенной нагрузки.
        """
        # 1. Берем все подтвержденные или временные распределения
        assignments = AssignmentResult.objects.all()
        rooms = Room.objects.filter(is_active=True).order_by('-capacity')
        
        # 2. Очищаем старые сессии (для демо-режима или пересчета)
        # ClassSession.objects.all().delete() # Опасно, лучше фильтр

        # 3. Алгоритм распределения по слотам
        for assignment in assignments:
            course = assignment.course
            teacher = assignment.teacher
            
            # Находим профиль курса для понимания кол-ва занятий
            total_hours = course.scheduler_profile.target_hours
            
            # РАСЧЕТ НЕДЕЛЬНОЙ НАГРУЗКИ (для недели):
            # 32 часа в семестр / 16 недель / 2 часа за пару = 1 пара в неделю.
            # 64 часа в семестр / 16 недель / 2 часа за пару = 2 пары в неделю.
            sessions_needed = max(1, (total_hours // 2) // 16) 
            
            groups = course.study_groups.all()
            if not groups.exists():
                ScheduleConflict.objects.create(severity='error', message=f"Курс '{course.title}' не привязан ни к одной группе.")
                continue

            sessions_created = 0
            # Перебор дней
            for day_offset in range(self.days_to_plan):
                if sessions_created >= sessions_needed: break
                
                current_day = self.start_date + timedelta(days=day_offset)
                day_sessions_for_this_course = 0 # Лимит на день
                
                # Перебор слотов
                for slot_start, slot_end in self.slots:
                    if sessions_created >= sessions_needed: break
                    if day_sessions_for_this_course >= 2: break # Не более 2-х пар одного предмета в день
                    
                    dt_start = timezone.make_aware(datetime.combine(current_day, slot_start))
                    dt_end = timezone.make_aware(datetime.combine(current_day, slot_end))

                    # Проверка конфликтов:
                    # 1. Свободен ли преподаватель?
                    if ClassSession.objects.filter(teacher=teacher, starts_at=dt_start).exists():
                        continue
                    
                    # 2. Свободны ли группы?
                    group_conflict = False
                    for group in groups:
                        if ClassSession.objects.filter(course__study_groups=group, starts_at=dt_start).exists():
                            group_conflict = True
                            break
                    if group_conflict: continue

                    # 3. Поиск свободной аудитории
                    suitable_room = None
                    max_students = max([g.scheduler_profile.student_count for g in groups] or [0])
                    
                    for room in rooms:
                        if room.capacity >= max_students:
                            if not ClassSession.objects.filter(room_ref=room, starts_at=dt_start).exists():
                                suitable_room = room
                                break
                    
                    if suitable_room:
                        # Создаем занятие
                        ClassSession.objects.create(
                            course=course,
                            teacher=teacher,
                            starts_at=dt_start,
                            ends_at=dt_end,
                            room_ref=suitable_room,
                            room=f"{suitable_room.name}"
                        )
                        sessions_created += 1
                        day_sessions_for_this_course += 1
                    
            if sessions_created < sessions_needed:
                ScheduleConflict.objects.create(
                    severity='warning', 
                    message=f"Не удалось полностью распределить курс '{course.title}' (создано {sessions_created}/{sessions_needed})."
                )

        return True
