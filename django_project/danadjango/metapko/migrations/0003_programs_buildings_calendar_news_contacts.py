# Generated manually for metapko extended domain

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metapko', '0002_domain_university_iiko'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudyProgram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='название программы')),
                ('code', models.CharField(blank=True, max_length=64, verbose_name='код / шифр')),
                (
                    'level',
                    models.CharField(
                        choices=[
                            ('bachelor', 'Бакалавриат'),
                            ('master', 'Магистратура'),
                            ('specialty', 'Специалитет'),
                            ('phd', 'Докторантура'),
                            ('other', 'Иное'),
                        ],
                        default='bachelor',
                        max_length=20,
                        verbose_name='уровень',
                    ),
                ),
                ('is_active', models.BooleanField(default=True, verbose_name='активна')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='порядок')),
            ],
            options={
                'verbose_name': 'учебная программа',
                'verbose_name_plural': 'учебные программы',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='StudyGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='группа / поток')),
                ('intake_year', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='год набора')),
                ('is_active', models.BooleanField(default=True, verbose_name='активна')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='порядок')),
                (
                    'program',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='groups',
                        to='metapko.studyprogram',
                        verbose_name='программа',
                    ),
                ),
            ],
            options={
                'verbose_name': 'учебная группа',
                'verbose_name_plural': 'учебные группы',
                'ordering': ['program', 'sort_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='название')),
                ('code', models.CharField(blank=True, max_length=32, verbose_name='краткое обозначение')),
                ('address', models.CharField(blank=True, max_length=512, verbose_name='адрес')),
                ('is_active', models.BooleanField(default=True, verbose_name='активен')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='порядок')),
            ],
            options={
                'verbose_name': 'корпус',
                'verbose_name_plural': 'корпуса',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='номер / название')),
                ('floor', models.SmallIntegerField(blank=True, null=True, verbose_name='этаж')),
                ('capacity', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='вместимость')),
                ('is_active', models.BooleanField(default=True, verbose_name='активна')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='порядок')),
                (
                    'building',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='rooms',
                        to='metapko.building',
                        verbose_name='корпус',
                    ),
                ),
            ],
            options={
                'verbose_name': 'аудитория',
                'verbose_name_plural': 'аудитории',
                'ordering': ['building', 'sort_order', 'name'],
                'unique_together': {('building', 'name')},
            },
        ),
        migrations.AddField(
            model_name='classsession',
            name='room_ref',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='class_sessions',
                to='metapko.room',
                verbose_name='аудитория (справочник)',
            ),
        ),
        migrations.AlterField(
            model_name='classsession',
            name='room',
            field=models.CharField(
                blank=True,
                help_text='если нет в справочнике',
                max_length=64,
                verbose_name='аудитория (текст)',
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='study_groups',
            field=models.ManyToManyField(
                blank=True,
                related_name='courses',
                to='metapko.studygroup',
                verbose_name='учебные группы',
            ),
        ),
        migrations.CreateModel(
            name='CalendarEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='заголовок')),
                (
                    'kind',
                    models.CharField(
                        choices=[
                            ('session_period', 'Учебная сессия / модуль'),
                            ('holiday', 'Каникулы / праздник'),
                            ('deadline', 'Дедлайн'),
                        ],
                        max_length=32,
                        verbose_name='тип',
                    ),
                ),
                ('starts_on', models.DateField(verbose_name='дата начала')),
                ('ends_on', models.DateField(blank=True, null=True, verbose_name='дата окончания')),
                ('description', models.TextField(blank=True, verbose_name='описание')),
                ('is_published', models.BooleanField(default=True, verbose_name='показывать в API')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='порядок')),
            ],
            options={
                'verbose_name': 'событие календаря',
                'verbose_name_plural': 'календарь',
                'ordering': ['starts_on', 'sort_order', 'id'],
            },
        ),
        migrations.AddIndex(
            model_name='calendarevent',
            index=models.Index(fields=['starts_on', 'kind'], name='metapko_cal_starts__e2ce53_idx'),
        ),
        migrations.CreateModel(
            name='NewsPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='заголовок')),
                ('slug', models.SlugField(blank=True, max_length=280, verbose_name='slug')),
                ('summary', models.CharField(blank=True, max_length=500, verbose_name='кратко')),
                ('body', models.TextField(blank=True, verbose_name='текст')),
                ('published_at', models.DateTimeField(blank=True, null=True, verbose_name='дата публикации')),
                ('is_published', models.BooleanField(default=True, verbose_name='опубликовано')),
                ('is_pinned', models.BooleanField(default=False, verbose_name='закрепить')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='порядок')),
            ],
            options={
                'verbose_name': 'новость / объявление',
                'verbose_name_plural': 'новости и объявления',
                'ordering': ['-is_pinned', '-published_at', 'sort_order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ContactEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='название подразделения')),
                (
                    'role_hint',
                    models.CharField(
                        blank=True,
                        help_text='например: деканат, методкабинет, техподдержка',
                        max_length=128,
                        verbose_name='тип (подсказка)',
                    ),
                ),
                ('phone', models.CharField(blank=True, max_length=64, verbose_name='телефон')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email')),
                ('address', models.CharField(blank=True, max_length=512, verbose_name='адрес / кабинет')),
                ('office_hours', models.CharField(blank=True, max_length=255, verbose_name='часы приёма')),
                ('notes', models.TextField(blank=True, verbose_name='примечание')),
                ('is_active', models.BooleanField(default=True, verbose_name='активна')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='порядок')),
            ],
            options={
                'verbose_name': 'контакт справочника',
                'verbose_name_plural': 'справочник контактов',
                'ordering': ['sort_order', 'title'],
            },
        ),
    ]
