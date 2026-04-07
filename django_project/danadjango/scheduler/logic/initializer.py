from metapko.models import Building, Room, Department, Teacher, StudyProgram, StudyGroup, Course
from scheduler.models import TeacherProfile, CourseProfile, GroupProfile

class SystemInitializer:
    @staticmethod
    def run_seed():
        """
        Создает базовый набор данных для работы генератора расписания.
        """
        stats = {'rooms': 0, 'groups': 0, 'courses': 0}
        
        # 1. Здание и Аудитории
        building, _ = Building.objects.get_or_create(name="Главный корпус", code="ГК")
        
        rooms_data = [
            ("101", 100), # Лекционная
            ("202", 30),  # Практика
            ("303", 25),  # ИТ-лаборатория
        ]
        for name, cap in rooms_data:
            room, created = Room.objects.get_or_create(building=building, name=name)
            if created or not room.capacity:
                room.capacity = cap
                room.save()
                stats['rooms'] += 1

        # 2. Кафедра
        dept, _ = Department.objects.get_or_create(name="Кафедра Информационных Технологий", code="ИТ")

        # 3. Программа и Группы
        program, _ = StudyProgram.objects.get_or_create(name="Computer Science", level=StudyProgram.Level.BACHELOR)
        
        groups_data = ["CS-101", "CS-102"]
        for g_name in groups_data:
            group, created = StudyGroup.objects.get_or_create(name=g_name, program=program)
            if created:
                GroupProfile.objects.get_or_create(group=group, student_count=20)
                stats['groups'] += 1

        # 4. Преподаватели (ППС)
        teachers_data = [
            ("Бутакова Марина Владимировна", "PhD", 1.0),
            ("Иванов Иван Иванович", "none", 1.0),
            ("Садвакасова Мадина", "assoc_prof", 1.0),
        ]
        stats['teachers'] = 0
        for name, degree, rate in teachers_data:
            teacher, created = Teacher.objects.get_or_create(full_name=name)
            if created:
                TeacherProfile.objects.get_or_create(
                    teacher=teacher,
                    defaults={
                        'academic_degree': degree,
                        'employment_rate': rate
                    }
                )
                stats['teachers'] += 1

        # 5. Курсы
        courses_data = [
            ("Математический анализ", "MATH-101", 32, CourseProfile.CourseType.LECTURE),
            ("Алгоритмы и структуры данных", "ALGO-201", 32, CourseProfile.CourseType.PRACTICE),
            ("Веб-разработка (React/Django)", "WEB-301", 32, CourseProfile.CourseType.LAB),
            ("Основы Искусственного Интеллекта", "AI-401", 16, CourseProfile.CourseType.LECTURE),
            ("Этика в ИТ", "ETH-100", 16, CourseProfile.CourseType.PRACTICE),
        ]
        
        all_groups = StudyGroup.objects.filter(name__in=groups_data)
        
        for title, code, hours, c_type in courses_data:
            course, created = Course.objects.get_or_create(title=title, code=code)
            if created:
                course.study_groups.set(all_groups)
                CourseProfile.objects.update_or_create(
                    course=course,
                    defaults={
                        'target_hours': hours,
                        'course_type': c_type
                    }
                )
                stats['courses'] += 1
                
        return stats
