from __future__ import annotations

import hashlib
import secrets
from decimal import Decimal
from typing import Optional

from django.core.validators import MinValueValidator
from django.db import models


class IntegrationClient(models.Model):
    """Внешний клиент (бот, сервис мета-университета) с доступом к API metapko."""

    name = models.CharField('название', max_length=255)
    is_active = models.BooleanField('активен', default=True)
    key_hash = models.CharField('хеш ключа', max_length=64, editable=False, db_index=True)
    notes = models.TextField('заметки', blank=True)
    created_at = models.DateTimeField('создан', auto_now_add=True)
    last_used_at = models.DateTimeField('последнее использование', null=True, blank=True)

    class Meta:
        verbose_name = 'клиент интеграции'
        verbose_name_plural = 'клиенты интеграции'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @staticmethod
    def hash_key(raw: str) -> str:
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def set_key(self, raw: str) -> None:
        self.key_hash = self.hash_key(raw)

    @classmethod
    def verify_key(cls, raw: str) -> Optional['IntegrationClient']:
        if not raw:
            return None
        digest = cls.hash_key(raw)
        return cls.objects.filter(key_hash=digest, is_active=True).first()

    @staticmethod
    def generate_raw_key() -> str:
        return secrets.token_urlsafe(32)


# ——— Meta-университет (вуз) ———


class Department(models.Model):
    """Кафедра / подразделение вуза."""

    name = models.CharField('название', max_length=255)
    code = models.CharField('код', max_length=32, blank=True)
    is_active = models.BooleanField('активна', default=True)
    sort_order = models.PositiveSmallIntegerField('порядок', default=0)

    class Meta:
        verbose_name = 'кафедра'
        verbose_name_plural = 'кафедры'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Teacher(models.Model):
    """Преподаватель."""

    full_name = models.CharField('ФИО', max_length=255)
    department = models.ForeignKey(
        Department,
        verbose_name='кафедра',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teachers',
    )
    position = models.CharField('должность', max_length=255, blank=True)
    email = models.EmailField('email', blank=True)
    phone = models.CharField('телефон', max_length=32, blank=True)
    is_active = models.BooleanField('активен', default=True)

    class Meta:
        verbose_name = 'преподаватель'
        verbose_name_plural = 'преподаватели'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class StudyProgram(models.Model):
    """Образовательная программа (например, направление бакалавриата)."""

    class Level(models.TextChoices):
        BACHELOR = 'bachelor', 'Бакалавриат'
        MASTER = 'master', 'Магистратура'
        SPECIALTY = 'specialty', 'Специалитет'
        PHD = 'phd', 'Докторантура'
        OTHER = 'other', 'Иное'

    name = models.CharField('название программы', max_length=255)
    code = models.CharField('код / шифр', max_length=64, blank=True)
    level = models.CharField(
        'уровень',
        max_length=20,
        choices=Level.choices,
        default=Level.BACHELOR,
    )
    is_active = models.BooleanField('активна', default=True)
    sort_order = models.PositiveSmallIntegerField('порядок', default=0)

    class Meta:
        verbose_name = 'учебная программа'
        verbose_name_plural = 'учебные программы'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class StudyGroup(models.Model):
    """Учебная группа / поток в рамках программы."""

    name = models.CharField('группа / поток', max_length=64)
    program = models.ForeignKey(
        StudyProgram,
        verbose_name='программа',
        on_delete=models.CASCADE,
        related_name='groups',
    )
    intake_year = models.PositiveSmallIntegerField('год набора', null=True, blank=True)
    is_active = models.BooleanField('активна', default=True)
    sort_order = models.PositiveSmallIntegerField('порядок', default=0)

    class Meta:
        verbose_name = 'учебная группа'
        verbose_name_plural = 'учебные группы'
        ordering = ['program', 'sort_order', 'name']

    def __str__(self):
        return f'{self.name} ({self.program})'


class Course(models.Model):
    """Учебный курс / дисциплина."""

    title = models.CharField('название', max_length=255)
    code = models.CharField('код курса', max_length=64, blank=True)
    description = models.TextField('описание', blank=True)
    teacher = models.ForeignKey(
        Teacher,
        verbose_name='преподаватель',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
    )
    study_groups = models.ManyToManyField(
        StudyGroup,
        verbose_name='учебные группы',
        related_name='courses',
        blank=True,
    )
    is_active = models.BooleanField('активен', default=True)

    class Meta:
        verbose_name = 'курс'
        verbose_name_plural = 'курсы'
        ordering = ['title']

    def __str__(self):
        return self.title


class Building(models.Model):
    """Корпус / здание."""

    name = models.CharField('название', max_length=255)
    code = models.CharField('краткое обозначение', max_length=32, blank=True)
    address = models.CharField('адрес', max_length=512, blank=True)
    is_active = models.BooleanField('активен', default=True)
    sort_order = models.PositiveSmallIntegerField('порядок', default=0)

    class Meta:
        verbose_name = 'корпус'
        verbose_name_plural = 'корпуса'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.code or self.name


class Room(models.Model):
    """Аудитория (справочник)."""

    building = models.ForeignKey(
        Building,
        verbose_name='корпус',
        on_delete=models.CASCADE,
        related_name='rooms',
    )
    name = models.CharField('номер / название', max_length=64)
    floor = models.SmallIntegerField('этаж', null=True, blank=True)
    capacity = models.PositiveSmallIntegerField('вместимость', null=True, blank=True)
    is_active = models.BooleanField('активна', default=True)
    sort_order = models.PositiveSmallIntegerField('порядок', default=0)

    class Meta:
        verbose_name = 'аудитория'
        verbose_name_plural = 'аудитории'
        ordering = ['building', 'sort_order', 'name']
        unique_together = [('building', 'name')]

    def __str__(self):
        return f'{self.building.code or self.building.name} — {self.name}'


class ClassSession(models.Model):
    """Занятие (слот в расписании)."""

    course = models.ForeignKey(
        Course,
        verbose_name='курс',
        on_delete=models.CASCADE,
        related_name='sessions',
    )
    title = models.CharField('тема занятия', max_length=255, blank=True)
    teacher = models.ForeignKey(
        Teacher,
        verbose_name='преподаватель',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_sessions',
    )
    starts_at = models.DateTimeField('начало')
    ends_at = models.DateTimeField('конец')
    room_ref = models.ForeignKey(
        Room,
        verbose_name='аудитория (справочник)',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_sessions',
    )
    room = models.CharField(
        'аудитория (текст)',
        max_length=64,
        blank=True,
        help_text='если нет в справочнике',
    )
    notes = models.TextField('заметки', blank=True)

    class Meta:
        verbose_name = 'занятие'
        verbose_name_plural = 'занятия'
        ordering = ['starts_at']
        indexes = [
            models.Index(fields=['starts_at']),
        ]

    def __str__(self):
        return f'{self.course.title} @ {self.starts_at}'


class FaqEntry(models.Model):
    """Справка для бота (FAQ)."""

    question = models.CharField('вопрос', max_length=500)
    answer = models.TextField('ответ')
    keywords = models.CharField(
        'ключевые слова',
        max_length=500,
        blank=True,
        help_text='через запятую, для подсказок поиска',
    )
    sort_order = models.PositiveSmallIntegerField('порядок', default=0)
    is_active = models.BooleanField('активен', default=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.question[:80]


class CalendarEvent(models.Model):
    """Календарь: сессия, каникулы, дедлайны."""

    class Kind(models.TextChoices):
        SESSION_PERIOD = 'session_period', 'Учебная сессия / модуль'
        HOLIDAY = 'holiday', 'Каникулы / праздник'
        DEADLINE = 'deadline', 'Дедлайн'

    title = models.CharField('заголовок', max_length=255)
    kind = models.CharField('тип', max_length=32, choices=Kind.choices)
    starts_on = models.DateField('дата начала')
    ends_on = models.DateField('дата окончания', null=True, blank=True)
    description = models.TextField('описание', blank=True)
    is_published = models.BooleanField('показывать в API', default=True)
    sort_order = models.PositiveSmallIntegerField('порядок', default=0)

    class Meta:
        verbose_name = 'событие календаря'
        verbose_name_plural = 'календарь'
        ordering = ['starts_on', 'sort_order', 'id']
        indexes = [models.Index(fields=['starts_on', 'kind'])]

    def __str__(self):
        return self.title


class NewsPost(models.Model):
    """Новость / объявление вуза."""

    title = models.CharField('заголовок', max_length=255)
    slug = models.SlugField('slug', max_length=280, blank=True)
    summary = models.CharField('кратко', max_length=500, blank=True)
    body = models.TextField('текст', blank=True)
    published_at = models.DateTimeField('дата публикации', null=True, blank=True)
    is_published = models.BooleanField('опубликовано', default=True)
    is_pinned = models.BooleanField('закрепить', default=False)
    sort_order = models.PositiveSmallIntegerField('порядок', default=0)

    class Meta:
        verbose_name = 'новость / объявление'
        verbose_name_plural = 'новости и объявления'
        ordering = ['-is_pinned', '-published_at', 'sort_order', 'id']

    def __str__(self):
        return self.title


class ContactEntry(models.Model):
    """Контакт справочника (деканат, методкабинет и т.д.)."""

    title = models.CharField('название подразделения', max_length=255)
    role_hint = models.CharField(
        'тип (подсказка)',
        max_length=128,
        blank=True,
        help_text='например: деканат, методкабинет, техподдержка',
    )
    phone = models.CharField('телефон', max_length=64, blank=True)
    email = models.EmailField('email', blank=True)
    address = models.CharField('адрес / кабинет', max_length=512, blank=True)
    office_hours = models.CharField('часы приёма', max_length=255, blank=True)
    notes = models.TextField('примечание', blank=True)
    is_active = models.BooleanField('активна', default=True)
    sort_order = models.PositiveSmallIntegerField('порядок', default=0)

    class Meta:
        verbose_name = 'контакт справочника'
        verbose_name_plural = 'справочник контактов'
        ordering = ['sort_order', 'title']

    def __str__(self):
        return self.title


# ——— Упрощённый контур IIKO (своя БД, без реального API iiko) ———


class IikoOutlet(models.Model):
    """Точка / подразделение (как филиал в IIKO)."""

    name = models.CharField('название', max_length=255)
    address = models.CharField('адрес', max_length=512, blank=True)
    phone = models.CharField('телефон', max_length=32, blank=True)
    is_active = models.BooleanField('активна', default=True)

    class Meta:
        verbose_name = 'точка (IIKO)'
        verbose_name_plural = 'точки (IIKO)'
        ordering = ['name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Позиция меню / номенклатура."""

    outlet = models.ForeignKey(
        IikoOutlet,
        verbose_name='точка',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='menu_items',
        help_text='пусто — общее меню для всех точек',
    )
    name = models.CharField('название', max_length=255)
    category = models.CharField('категория', max_length=128, blank=True)
    price = models.DecimalField(
        'цена',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
    )
    is_available = models.BooleanField('доступно', default=True)
    sort_order = models.PositiveSmallIntegerField('порядок', default=0)

    class Meta:
        verbose_name = 'блюдо / позиция'
        verbose_name_plural = 'меню / номенклатура'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class CustomerOrder(models.Model):
    """Упрощённый заказ (имитация без обращения к API IIKO)."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'новый'
        CONFIRMED = 'confirmed', 'подтверждён'
        PREPARING = 'preparing', 'готовится'
        DONE = 'done', 'выдан'
        CANCELLED = 'cancelled', 'отменён'

    outlet = models.ForeignKey(
        IikoOutlet,
        verbose_name='точка',
        on_delete=models.CASCADE,
        related_name='orders',
    )
    status = models.CharField(
        'статус',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    customer_name = models.CharField('имя клиента', max_length=255, blank=True)
    phone = models.CharField('телефон', max_length=32, blank=True)
    notes = models.TextField('комментарий', blank=True)
    external_ref = models.CharField('внешний номер', max_length=64, blank=True)
    created_at = models.DateTimeField('создан', auto_now_add=True)
    updated_at = models.DateTimeField('обновлён', auto_now=True)

    class Meta:
        verbose_name = 'заказ (IIKO mock)'
        verbose_name_plural = 'заказы (IIKO mock)'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f'Заказ #{self.pk} ({self.get_status_display()})'


class OrderLine(models.Model):
    """Строка заказа."""

    order = models.ForeignKey(
        CustomerOrder,
        verbose_name='заказ',
        on_delete=models.CASCADE,
        related_name='lines',
    )
    menu_item = models.ForeignKey(
        MenuItem,
        verbose_name='позиция меню',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    dish_name = models.CharField('название', max_length=255)
    quantity = models.PositiveSmallIntegerField('кол-во', default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        'цена за ед.',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
    )

    class Meta:
        verbose_name = 'строка заказа'
        verbose_name_plural = 'строки заказа'

    def __str__(self):
        return f'{self.dish_name} × {self.quantity}'


class ServiceTicket(models.Model):
    """Заявка / задача в очереди (уведомления, обращения)."""

    class Status(models.TextChoices):
        NEW = 'new', 'новая'
        IN_PROGRESS = 'in_progress', 'в работе'
        DONE = 'done', 'выполнена'
        CANCELLED = 'cancelled', 'отменена'

    class Priority(models.TextChoices):
        LOW = 'low', 'низкий'
        NORMAL = 'normal', 'обычный'
        HIGH = 'high', 'высокий'

    title = models.CharField('заголовок', max_length=255)
    description = models.TextField('описание', blank=True)
    outlet = models.ForeignKey(
        IikoOutlet,
        verbose_name='точка',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_tickets',
    )
    status = models.CharField(
        'статус',
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    priority = models.CharField(
        'приоритет',
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    requester_name = models.CharField('кто обратился', max_length=255, blank=True)
    contact = models.CharField('контакт', max_length=255, blank=True)
    created_at = models.DateTimeField('создана', auto_now_add=True)
    updated_at = models.DateTimeField('обновлена', auto_now=True)

    class Meta:
        verbose_name = 'заявка'
        verbose_name_plural = 'заявки'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return self.title
