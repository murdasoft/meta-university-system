import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metapko', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='название')),
                ('code', models.CharField(blank=True, max_length=32, verbose_name='код')),
                ('is_active', models.BooleanField(default=True, verbose_name='активна')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='порядок')),
            ],
            options={
                'verbose_name': 'кафедра',
                'verbose_name_plural': 'кафедры',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='IikoOutlet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='название')),
                ('address', models.CharField(blank=True, max_length=512, verbose_name='адрес')),
                ('phone', models.CharField(blank=True, max_length=32, verbose_name='телефон')),
                ('is_active', models.BooleanField(default=True, verbose_name='активна')),
            ],
            options={
                'verbose_name': 'точка (IIKO)',
                'verbose_name_plural': 'точки (IIKO)',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, verbose_name='ФИО')),
                ('position', models.CharField(blank=True, max_length=255, verbose_name='должность')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email')),
                ('phone', models.CharField(blank=True, max_length=32, verbose_name='телефон')),
                ('is_active', models.BooleanField(default=True, verbose_name='активен')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teachers', to='metapko.department', verbose_name='кафедра')),
            ],
            options={
                'verbose_name': 'преподаватель',
                'verbose_name_plural': 'преподаватели',
                'ordering': ['full_name'],
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='название')),
                ('code', models.CharField(blank=True, max_length=64, verbose_name='код курса')),
                ('description', models.TextField(blank=True, verbose_name='описание')),
                ('is_active', models.BooleanField(default=True, verbose_name='активен')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='courses', to='metapko.teacher', verbose_name='преподаватель')),
            ],
            options={
                'verbose_name': 'курс',
                'verbose_name_plural': 'курсы',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='ClassSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='тема занятия')),
                ('starts_at', models.DateTimeField(verbose_name='начало')),
                ('ends_at', models.DateTimeField(verbose_name='конец')),
                ('room', models.CharField(blank=True, max_length=64, verbose_name='аудитория')),
                ('notes', models.TextField(blank=True, verbose_name='заметки')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='metapko.course', verbose_name='курс')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='class_sessions', to='metapko.teacher', verbose_name='преподаватель')),
            ],
            options={
                'verbose_name': 'занятие',
                'verbose_name_plural': 'занятия',
                'ordering': ['starts_at'],
            },
        ),
        migrations.AddIndex(
            model_name='classsession',
            index=models.Index(fields=['starts_at'], name='metapko_cla_starts__idx'),
        ),
        migrations.CreateModel(
            name='FaqEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=500, verbose_name='вопрос')),
                ('answer', models.TextField(verbose_name='ответ')),
                ('keywords', models.CharField(blank=True, help_text='через запятую, для подсказок поиска', max_length=500, verbose_name='ключевые слова')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='активен')),
            ],
            options={
                'verbose_name': 'FAQ',
                'verbose_name_plural': 'FAQ',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='название')),
                ('category', models.CharField(blank=True, max_length=128, verbose_name='категория')),
                ('price', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='цена')),
                ('is_available', models.BooleanField(default=True, verbose_name='доступно')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='порядок')),
                ('outlet', models.ForeignKey(blank=True, help_text='пусто — общее меню для всех точек', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='metapko.iikooutlet', verbose_name='точка')),
            ],
            options={
                'verbose_name': 'блюдо / позиция',
                'verbose_name_plural': 'меню / номенклатура',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CustomerOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'новый'), ('confirmed', 'подтверждён'), ('preparing', 'готовится'), ('done', 'выдан'), ('cancelled', 'отменён')], default='pending', max_length=20, verbose_name='статус')),
                ('customer_name', models.CharField(blank=True, max_length=255, verbose_name='имя клиента')),
                ('phone', models.CharField(blank=True, max_length=32, verbose_name='телефон')),
                ('notes', models.TextField(blank=True, verbose_name='комментарий')),
                ('external_ref', models.CharField(blank=True, max_length=64, verbose_name='внешний номер')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='обновлён')),
                ('outlet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='metapko.iikooutlet', verbose_name='точка')),
            ],
            options={
                'verbose_name': 'заказ (IIKO mock)',
                'verbose_name_plural': 'заказы (IIKO mock)',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dish_name', models.CharField(max_length=255, verbose_name='название')),
                ('quantity', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='кол-во')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='цена за ед.')),
                ('menu_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='metapko.menuitem', verbose_name='позиция меню')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='metapko.customerorder', verbose_name='заказ')),
            ],
            options={
                'verbose_name': 'строка заказа',
                'verbose_name_plural': 'строки заказа',
            },
        ),
        migrations.AddIndex(
            model_name='customerorder',
            index=models.Index(fields=['status', '-created_at'], name='metapko_cus_status__idx'),
        ),
        migrations.CreateModel(
            name='ServiceTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='заголовок')),
                ('description', models.TextField(blank=True, verbose_name='описание')),
                ('status', models.CharField(choices=[('new', 'новая'), ('in_progress', 'в работе'), ('done', 'выполнена'), ('cancelled', 'отменена')], default='new', max_length=20, verbose_name='статус')),
                ('priority', models.CharField(choices=[('low', 'низкий'), ('normal', 'обычный'), ('high', 'высокий')], default='normal', max_length=20, verbose_name='приоритет')),
                ('requester_name', models.CharField(blank=True, max_length=255, verbose_name='кто обратился')),
                ('contact', models.CharField(blank=True, max_length=255, verbose_name='контакт')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='создана')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='обновлена')),
                ('outlet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_tickets', to='metapko.iikooutlet', verbose_name='точка')),
            ],
            options={
                'verbose_name': 'заявка',
                'verbose_name_plural': 'заявки',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='serviceticket',
            index=models.Index(fields=['status', '-created_at'], name='metapko_ser_status__idx'),
        ),
    ]
