"""Массовое наполнение metapko демо-данными (бот и API). Клиенты IntegrationClient не трогаем."""

from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from metapko.models import (
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
    OrderLine,
    Room,
    ServiceTicket,
    StudyGroup,
    StudyProgram,
    Teacher,
)


N = 12

DEPARTMENTS = [
    ('Кафедра информационных систем', 'ИС'),
    ('Кафедра математики и моделирования', 'МАТ'),
    ('Кафедра управления и сервиса', 'УИС'),
    ('Кафедра педагогики', 'ПЕД'),
    ('Кафедра языков и коммуникации', 'ЯК'),
    ('Кафедра экономики и финансов', 'ЭК'),
    ('Кафедра права и социальных наук', 'ПР'),
    ('Кафедра дизайна и медиа', 'ДМ'),
    ('Кафедра химии и биотехнологий', 'ХБ'),
    ('Кафедра физической культуры', 'ФК'),
    ('Кафедра туризма и гостеприимства', 'ТГ'),
    ('Центр цифрового образования', 'ЦЦО'),
]

PROGRAMS = [
    ('Прикладная информатика', '6В05309', StudyProgram.Level.BACHELOR),
    ('Математическое моделирование', '6В05401', StudyProgram.Level.BACHELOR),
    ('Гостиничное дело', '6В11108', StudyProgram.Level.BACHELOR),
    ('Педагогическое образование', '6В01901', StudyProgram.Level.BACHELOR),
    ('Экономика', '6В04103', StudyProgram.Level.BACHELOR),
    ('Право', '6В04212', StudyProgram.Level.BACHELOR),
    ('Дизайн', '6В02102', StudyProgram.Level.BACHELOR),
    ('Биотехнология', '6В01502', StudyProgram.Level.BACHELOR),
    ('Физическая культура', '6В10102', StudyProgram.Level.BACHELOR),
    ('Туризм', '6В11106', StudyProgram.Level.BACHELOR),
    ('Цифровая инженерия', '6В05310', StudyProgram.Level.BACHELOR),
    ('Искусственный интеллект (маг.)', '7М05309', StudyProgram.Level.MASTER),
]

GROUP_NAMES = [
    'ПИ-21-1', 'ММ-21-2', 'ГД-22-1', 'ПОД-20-3', 'ЭК-21-1', 'ПР-22-2',
    'ДЗ-21-1', 'БТ-22-1', 'ФК-20-2', 'ТУР-21-3', 'ЦИ-22-1', 'ИИ-23-1м',
]

BUILDINGS = [
    ('Главный учебный корпус', 'А', 'пр. Абая, 1'),
    ('Корпус естественных наук', 'Б', 'ул. Научная, 15'),
    ('Спортивный комплекс', 'СК', 'ул. Спортивная, 2'),
    ('Общежитие / буфет', 'О', 'ул. Студенческая, 9'),
]

# (building_index 0..3, room_name, floor, capacity)
ROOMS = [
    (0, '204', 2, 40),
    (0, '301', 3, 60),
    (0, 'Актовый зал', 1, 200),
    (1, '105', 1, 30),
    (1, 'Лаб. 2', 2, 24),
    (1, '410', 4, 45),
    (2, 'Зал игровых', 1, 80),
    (2, 'Секретариат', 1, 8),
    (3, 'Столовая', 1, 120),
    (0, 'Б-101', 1, 35),
    (0, 'Коворкинг', 2, 50),
    (1, '207', 2, 28),
]

TEACHERS = [
    ('Әлия Серікқызы Нұрланова', 'доцент'),
    ('Ерлан Болатұлы Омаров', 'ст. преподаватель'),
    ('Мария Ивановна Ким', 'профессор'),
    ('Дәулет Нұрланұлы Сысенов', 'доцент'),
    ('Анна Петровна Волкова', 'ст. преподаватель'),
    ('Руслан Әмірұлы Жәнібеков', 'преподаватель'),
    ('Светлана Омарқызы Әбдірахманова', 'доцент'),
    ('Тимур Қасымұлы Ерғали', 'ст. преподаватель'),
    ('Гульнара Рахимовна Оспанова', 'профессор'),
    ('Асхат Маратұлы Бекмұратов', 'преподаватель'),
    ('Елена Сергеевна Нуртазина', 'ст. преподаватель'),
    ('Нұрдәулет Ерболұлы Сағындық', 'доцент'),
]

COURSES = [
    ('Интеграция информационных систем', 'ИС-405', 'API, шлюзы, Telegram-боты в вузе.'),
    ('Математическое моделирование', 'МАТ-301', 'Модели процессов и симуляции.'),
    ('Управление сервисами общественного питания', 'УП-210', 'Процессы зала и кассы, учебный контур IIKO.'),
    ('Педагогическая психология', 'ПЕД-120', 'Мотивация и обратная связь в обучении.'),
    ('Академическое письмо', 'ЯК-202', 'Научный стиль и цитирование.'),
    ('Корпоративные финансы', 'ЭК-330', 'Бюджетирование учебных проектов.'),
    ('Основы гражданского права', 'ПР-214', 'Договоры и персональные данные.'),
    ('Визуальная коммуникация', 'ДМ-156', 'UI/UX для образовательных сервисов.'),
    ('Биохимия питания', 'ХБ-188', 'Состав блюд и нормативы.'),
    ('Менеджмент качества в спорте', 'ФК-240', 'Стандарты площадок и расписаний.'),
    ('Гостиничный сервис', 'ТГ-275', 'Стандарты приёма и коммуникации гостя.'),
    ('Цифровая грамотность персонала', 'ЦЦО-101', 'Безопасность учетных записей и API-ключей.'),
]

SESSION_TOPICS = [
    'Введение и цели модуля',
    'Практикум: проектирование API',
    'Разбор кейса и Q&A',
    'Лабораторная: моделирование',
    'Гостевой доклад и обсуждение',
    'Процессы зала: роли персонала',
    'Тестирование и ретроспектива',
    'Семинар: групповая работа',
    'Итоговая аттестация (консультация)',
    'Документооборот и SLA',
    'Безопасность и журналирование',
    'Демо-защита проектов',
]

FAQ_SEED = [
    ('Как узнать расписание занятий?', 'В Telegram-боте используйте команду /sessions — данные берутся из портала Meta-университета.', 'расписание,бот,sessions'),
    ('Как связаться с преподавателем?', 'Список преподавателей: /teachers в боте; контакты указаны в карточке, если внесены в систему.', 'teacher,контакт,преподаватель'),
    ('Что такое точка IIKO в портале?', 'Это учебная модель точки общепита; реальная интеграция с IIKO подключается отдельно.', 'iiko,точка'),
    ('Где взять ключ API для бота?', 'В meta-admin: «Клиенты интеграции» — выпуск ключа только для staff.', 'api,ключ,meta-admin'),
    ('Как добавить новое занятие?', 'Портал /metapko/dashboard/ → «Занятие», либо через meta-admin.', 'занятие,добавить'),
    ('Поддержка: куда писать?', 'Заявки можно заводить через API заявок или связаться с администратором вуза.', 'поддержка,заявка'),
    ('Часы работы столовой (демо)?', 'В учебных данных указаны в карточке точки; уточняйте у администрации корпуса.', 'столовая,часы'),
    ('Оплата в системе учебной — реальная?', 'Нет, заказы в контуре mock; для реальной оплаты нужна внешняя касса.', 'оплата,заказ'),
    ('Как искать в FAQ?', 'Команда /faq в боте; вопросы индексируются по ключевым словам.', 'faq,бот'),
    ('Можно ли выгрузить меню?', 'Да, через REST /api/metapko/v1/ с ключом клиента интеграции.', 'меню,api'),
    ('Где хранятся персональные данные?', 'В базе приложения; доступ только у staff и по ролям; ключи API хешируются.', 'персональные,безопасность'),
    ('Как обновить описание курса?', 'meta-admin → Курсы, или попросите staff внести через портал быстрого добавления.', 'курс,описание'),
]

OUTLETS = [
    ('Столовая главного корпуса', 'г. Алматы, пр. Абая, уч. корпус А', '+7 727 111 01 01'),
    ('Кафе библиотечного крыла', 'г. Алматы, ул. Научная, корпус Б', '+7 727 111 02 02'),
    ('Buffet инженерного факультета', 'г. Алматы, корпус В, 1 этаж', '+7 727 111 03 03'),
    ('Столовая общежития №2', 'г. Алматы, общежитие, блок столовой', '+7 727 111 04 04'),
    ('Кофе-поинт Meta Lab', 'г. Алматы, лабораторный корпус', '+7 727 111 05 05'),
    ('Точка «Универсам» (демо)', 'г. Алматы, учебная улица 10', '+7 727 111 06 06'),
    ('Касса спорткомплекса', 'г. Алматы, СК университета', '+7 727 111 07 07'),
    ('Летняя терраса', 'г. Алматы, внутренний двор', '+7 727 111 08 08'),
    ('Ночной буфет (пилот)', 'г. Алматы, коворкинг 24/7', '+7 727 111 09 09'),
    ('Автомат с напитками', 'ул. Научная, холл 3', ''),
    ('Точка выдачи предзаказов', 'Корпус А, вход с торца', '+7 727 111 10 10'),
    ('Учебная кухня', 'Корпус Г, ауд. 12', '+7 727 111 11 11'),
]

MENU_ITEMS = [
    ('Комплекс обеденный №1', 'Комплексы', '1290'),
    ('Комплекс вегетарианский', 'Комплексы', '1190'),
    ('Борщ + салат', 'Первое и салат', '950'),
    ('Плов с говядиной', 'Горячее', '1350'),
    ('Котлета куриная с гарниром', 'Горячее', '890'),
    ('Салат «Цезарь»', 'Салаты', '780'),
    ('Чай чёрный 200 мл', 'Напитки', '150'),
    ('Кофе американо', 'Напитки', '450'),
    ('Вода 0.5', 'Напитки', '200'),
    ('Выпечка дня', 'Десерты', '320'),
    ('Сок 200 мл', 'Напитки', '280'),
    ('Суп дня', 'Первое', '520'),
]

CALENDAR_SEED = [
    ('Весенние каникулы', CalendarEvent.Kind.HOLIDAY),
    ('Модуль 2 — зачётная неделя', CalendarEvent.Kind.SESSION_PERIOD),
    ('Дедлайн подачи курсовых (весна)', CalendarEvent.Kind.DEADLINE),
    ('День университета', CalendarEvent.Kind.HOLIDAY),
    ('Летняя экзаменационная сессия', CalendarEvent.Kind.SESSION_PERIOD),
    ('Дедлайн заявок на практику', CalendarEvent.Kind.DEADLINE),
    ('Осенние каникулы', CalendarEvent.Kind.HOLIDAY),
    ('НИО — промежуточный отчёт', CalendarEvent.Kind.DEADLINE),
    ('Зимняя экзаменационная сессия', CalendarEvent.Kind.SESSION_PERIOD),
    ('День открытых дверей (мета)', CalendarEvent.Kind.HOLIDAY),
    ('Защита ВКР магистров', CalendarEvent.Kind.DEADLINE),
    ('Учебно-тренировочные сборы', CalendarEvent.Kind.SESSION_PERIOD),
]

CONTACTS_SEED = [
    ('Деканат факультета цифровых технологий', 'деканат', '+7 727 200 01 01', 'dekanat.digital@meta-uni.local', 'корп. А, каб. 115', 'Пн–Чт 10:00–13:00'),
    ('Методический кабинет', 'методкабинет', '+7 727 200 01 02', 'method@meta-uni.local', 'корп. А, каб. 208', 'Вт–Пт 14:00–17:00'),
    ('Техническая поддержка LMS', 'техподдержка', '+7 700 000 99 99', 'support@meta-uni.local', 'онлайн / коворкинг', '24/7 тикеты'),
    ('Приёмная комиссия', 'приёмная', '+7 727 200 03 03', 'priem@meta-uni.local', 'корп. А, холл', 'сезон приёма'),
    ('Центр карьеры', 'карьера', '+7 727 200 04 04', 'career@meta-uni.local', 'корп. Б, 1 этаж', 'Пн–Ср 11:00–16:00'),
    ('Бухгалтерия (образовательные договоры)', 'бухгалтерия', '+7 727 200 05 05', 'fin@meta-uni.local', 'корп. А, каб. 312', 'Пн–Пт 09:00–12:00'),
    ('Отдел внеучебной работы', 'внеучебка', '+7 727 200 06 06', 'clubs@meta-uni.local', 'СК, 2 этаж', 'по расписанию клубов'),
    ('Медицинский пункт', 'медпункт', '+7 727 200 07 07', '', 'корп. А, цоколь', 'ежедневно 08:30–17:00'),
    ('Проектный офис Meta-университет', 'проекты', '+7 727 200 08 08', 'pmo@meta-uni.local', 'коворкинг', 'Пн–Чт 09:00–18:00'),
    ('Офис международных программ', 'международный', '+7 727 200 09 09', 'intl@meta-uni.local', 'корп. Б, 301', 'по записи'),
    ('Служба безопасности кампуса', 'безопасность', '+7 727 200 00 00', '', 'КПП главный', 'круглосуточно'),
    ('Библиотека (справочный стол)', 'библиотека', '+7 727 200 11 11', 'lib@meta-uni.local', 'корп. Б, холл', 'Пн–Сб 09:00–20:00'),
]


class Command(BaseCommand):
    help = (
        'Демо-данные metapko: программы, группы, корпуса, аудитории, курсы, занятия, календарь, новости, '
        'контакты, FAQ, IIKO. IntegrationClient не трогаем. --clear очищает доменные таблицы.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Удалить доменные данные metapko перед заполнением',
        )

    def handle(self, *args, **options):
        clear = options['clear']

        if not clear and Department.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    'В metapko уже есть кафедры. Повтор: python manage.py seed_metapko_bulk --clear',
                ),
            )
            return

        with transaction.atomic():
            if clear:
                n_orders = CustomerOrder.objects.count()
                n_lines = OrderLine.objects.count()
                n_tickets = ServiceTicket.objects.count()
                OrderLine.objects.all().delete()
                CustomerOrder.objects.all().delete()
                ServiceTicket.objects.all().delete()
                ClassSession.objects.all().delete()
                Course.objects.all().delete()
                Teacher.objects.all().delete()
                Department.objects.all().delete()
                StudyGroup.objects.all().delete()
                StudyProgram.objects.all().delete()
                Room.objects.all().delete()
                Building.objects.all().delete()
                CalendarEvent.objects.all().delete()
                NewsPost.objects.all().delete()
                ContactEntry.objects.all().delete()
                FaqEntry.objects.all().delete()
                MenuItem.objects.all().delete()
                IikoOutlet.objects.all().delete()
                self.stdout.write(
                    self.style.WARNING(
                        f'Очищено: заказы {n_orders}, строки {n_lines}, заявки {n_tickets}; '
                        'остальные доменные таблицы metapko.',
                    ),
                )

            depts = []
            for i in range(N):
                name, code = DEPARTMENTS[i]
                depts.append(
                    Department.objects.create(
                        name=name,
                        code=code,
                        sort_order=i + 1,
                        is_active=True,
                    ),
                )

            programs = []
            for i in range(N):
                name, code, level = PROGRAMS[i]
                programs.append(
                    StudyProgram.objects.create(
                        name=name,
                        code=code,
                        level=level,
                        sort_order=i + 1,
                        is_active=True,
                    ),
                )

            groups = []
            for i in range(N):
                groups.append(
                    StudyGroup.objects.create(
                        name=GROUP_NAMES[i],
                        program=programs[i],
                        intake_year=2020 + (i % 4),
                        sort_order=i + 1,
                        is_active=True,
                    ),
                )

            buildings = []
            for j, (bname, bcode, addr) in enumerate(BUILDINGS):
                buildings.append(
                    Building.objects.create(
                        name=bname,
                        code=bcode,
                        address=addr,
                        sort_order=j + 1,
                        is_active=True,
                    ),
                )

            rooms = []
            for j, (bi, rname, fl, cap) in enumerate(ROOMS):
                rooms.append(
                    Room.objects.create(
                        building=buildings[bi],
                        name=rname,
                        floor=fl,
                        capacity=cap,
                        sort_order=j + 1,
                        is_active=True,
                    ),
                )

            teachers = []
            for i in range(N):
                fn, pos = TEACHERS[i]
                dept = depts[i % len(depts)]
                teachers.append(
                    Teacher.objects.create(
                        full_name=fn,
                        department=dept,
                        position=pos,
                        email=f'teacher{i + 1:02d}@meta-uni.local',
                        phone=f'+7 700 100 {i + 10:02d} {i + 10:02d}',
                        is_active=True,
                    ),
                )

            courses = []
            for i in range(N):
                title, code, desc = COURSES[i]
                c = Course.objects.create(
                    title=title,
                    code=code,
                    description=desc,
                    teacher=teachers[i],
                    is_active=True,
                )
                c.study_groups.add(groups[i], groups[(i + 1) % N])
                courses.append(c)

            base = timezone.now().replace(hour=9, minute=30, second=0, microsecond=0)
            if base.weekday() >= 5:
                base += timedelta(days=(7 - base.weekday()))

            for i in range(N):
                course = courses[i]
                teacher = course.teacher
                day_offset = i // 2
                hour_bias = (i % 3) * 2
                starts = base + timedelta(days=day_offset, hours=hour_bias)
                ends = starts + timedelta(hours=1, minutes=30)
                ClassSession.objects.create(
                    course=course,
                    title=SESSION_TOPICS[i],
                    teacher=teacher,
                    starts_at=starts,
                    ends_at=ends,
                    room_ref=rooms[i % len(rooms)],
                    room='',
                    notes='Сгенерировано seed_metapko_bulk.',
                )

            for i in range(N):
                q, a, kw = FAQ_SEED[i]
                FaqEntry.objects.create(
                    question=q,
                    answer=a,
                    keywords=kw,
                    sort_order=i + 1,
                    is_active=True,
                )

            outlets = []
            for i in range(N):
                name, addr, phone = OUTLETS[i]
                outlets.append(
                    IikoOutlet.objects.create(
                        name=name,
                        address=addr,
                        phone=phone,
                        is_active=True,
                    ),
                )

            for i in range(N):
                name, cat, price_s = MENU_ITEMS[i]
                outlet = outlets[i % len(outlets)]
                MenuItem.objects.create(
                    outlet=outlet,
                    name=name,
                    category=cat,
                    price=Decimal(price_s),
                    is_available=True,
                    sort_order=i + 1,
                )

            today = timezone.now().date()
            for i in range(N):
                title, kind = CALENDAR_SEED[i]
                start = today + timedelta(days=i * 7 - 21)
                end = None
                if kind == CalendarEvent.Kind.HOLIDAY:
                    end = start + timedelta(days=4 if i % 2 == 0 else 2)
                elif kind == CalendarEvent.Kind.SESSION_PERIOD:
                    end = start + timedelta(days=13)
                CalendarEvent.objects.create(
                    title=title,
                    kind=kind,
                    starts_on=start,
                    ends_on=end,
                    description=f'Демо-событие {i + 1}.',
                    sort_order=i + 1,
                    is_published=True,
                )

            now = timezone.now()
            news_titles = [
                'Старт регистрации на летнюю практику',
                'Обновление расписания: модуль 2',
                'Гостевая лекция: API в образовании',
                'Конкурс студенческих проектов Meta Lab',
                'Изменение графика работы библиотеки',
                'Напоминание: дедлайн курсовых',
                'День карьеры — 15 участников индустрии',
                'Безопасность: смена Wi‑Fi пароля в общежитии',
                'Приглашаем на День открытых дверей',
                'Расширение меню столовой (пилот)',
                'Итоги зимней сессии опубликованы',
                'Новый корпоративный чат поддержки',
            ]
            for i in range(N):
                NewsPost.objects.create(
                    title=news_titles[i],
                    slug=f'news-demo-{i + 1}',
                    summary=f'Краткое описание новости {i + 1}.',
                    body=f'Полный текст объявления {i + 1}. Подробности на портале и в боте (/news).',
                    published_at=now - timedelta(days=N - i),
                    is_published=True,
                    is_pinned=(i == 0),
                    sort_order=i + 1,
                )

            for i, row in enumerate(CONTACTS_SEED):
                title, role, phone, email, addr, hours = row
                ContactEntry.objects.create(
                    title=title,
                    role_hint=role,
                    phone=phone,
                    email=email or '',
                    address=addr,
                    office_hours=hours,
                    notes='',
                    sort_order=i + 1,
                    is_active=True,
                )

        self.stdout.write(self.style.SUCCESS('Готово: полный демо-набор metapko (программы, аудитории, календарь, новости, контакты).'))
