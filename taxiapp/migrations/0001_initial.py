# Generated by Django 3.2.6 on 2022-10-31 11:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('slug', models.SlugField(blank=True, max_length=10, verbose_name='Url')),
                ('car_number', models.CharField(blank=True, default='', max_length=15, null=True, verbose_name='Номер')),
                ('car_brand', models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='Марка')),
                ('car_model', models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='Модель')),
            ],
            options={
                'verbose_name': 'Автомобиль',
                'verbose_name_plural': 'Автомобили',
            },
        ),
        migrations.CreateModel(
            name='Cost_item',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('slug', models.SlugField(blank=True, max_length=10, verbose_name='Url')),
                ('title', models.CharField(max_length=50, verbose_name='Наименование')),
                ('is_category', models.BooleanField(default=False, verbose_name='Это категория')),
                ('parent_item', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='taxiapp.cost_item', verbose_name='Родитель')),
            ],
            options={
                'verbose_name': 'Статья затрат',
                'verbose_name_plural': 'Статьи затрат',
            },
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=30, verbose_name='Имя')),
                ('second_name', models.CharField(max_length=30, verbose_name='Фамилия')),
                ('third_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='Отчество')),
                ('driver_license', models.CharField(blank=True, default='', max_length=15, null=True, verbose_name='Номер В/У')),
                ('car_number', models.CharField(blank=True, default='', max_length=15, null=True, verbose_name='Номер А/М')),
                ('car_model', models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='Марка А/М')),
                ('fuel_card', models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='Топливная карта')),
                ('fuel_card_2', models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='Топливная карта 2')),
                ('email', models.CharField(blank=True, max_length=30, verbose_name='Email')),
                ('rate', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, null=True, verbose_name='Ставка')),
                ('active', models.BooleanField(default=True, verbose_name='Активный')),
                ('slug', models.SlugField(blank=True, max_length=10, verbose_name='Url')),
                ('debt', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Долг')),
                ('monday', models.BooleanField(default=True, verbose_name='Понедельник')),
                ('tuesday', models.BooleanField(default=True, verbose_name='Вторник')),
                ('wednesday', models.BooleanField(default=True, verbose_name='Среда')),
                ('thursday', models.BooleanField(default=True, verbose_name='Четверг')),
                ('friday', models.BooleanField(default=True, verbose_name='Пятница')),
                ('saturday', models.BooleanField(default=True, verbose_name='Суббота')),
                ('sunday', models.BooleanField(default=True, verbose_name='Воскресенье')),
                ('car', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='taxiapp.car', verbose_name='Автомобиль')),
            ],
            options={
                'verbose_name': 'Водитель',
                'verbose_name_plural': 'Водители',
            },
        ),
        migrations.CreateModel(
            name='Working_day',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(verbose_name='Дата рабочего дня')),
                ('rate', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Ставка')),
                ('fuel', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='ГСМ')),
                ('penalties', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Штрафы')),
                ('cash', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Наличные')),
                ('cash_card', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Карта')),
                ('cashless', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Безналичные')),
                ('debt_of_day', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Долг дня')),
                ('slug', models.SlugField(blank=True, max_length=10, verbose_name='Url')),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='taxiapp.driver')),
            ],
            options={
                'verbose_name': 'Рабочий день',
                'verbose_name_plural': 'Рабочие дни',
            },
        ),
        migrations.CreateModel(
            name='HistoricalWorking_day',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('date', models.DateField(verbose_name='Дата рабочего дня')),
                ('rate', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Ставка')),
                ('fuel', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='ГСМ')),
                ('penalties', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Штрафы')),
                ('cash', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Наличные')),
                ('cash_card', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Карта')),
                ('cashless', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Безналичные')),
                ('debt_of_day', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Долг дня')),
                ('slug', models.SlugField(blank=True, max_length=10, verbose_name='Url')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('driver', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='taxiapp.driver')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Рабочий день',
                'verbose_name_plural': 'historical Рабочие дни',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalDriver',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='Имя')),
                ('second_name', models.CharField(max_length=30, verbose_name='Фамилия')),
                ('third_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='Отчество')),
                ('driver_license', models.CharField(blank=True, default='', max_length=15, null=True, verbose_name='Номер В/У')),
                ('car_number', models.CharField(blank=True, default='', max_length=15, null=True, verbose_name='Номер А/М')),
                ('car_model', models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='Марка А/М')),
                ('fuel_card', models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='Топливная карта')),
                ('fuel_card_2', models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='Топливная карта 2')),
                ('email', models.CharField(blank=True, max_length=30, verbose_name='Email')),
                ('rate', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, null=True, verbose_name='Ставка')),
                ('active', models.BooleanField(default=True, verbose_name='Активный')),
                ('slug', models.SlugField(blank=True, max_length=10, verbose_name='Url')),
                ('debt', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Долг')),
                ('monday', models.BooleanField(default=True, verbose_name='Понедельник')),
                ('tuesday', models.BooleanField(default=True, verbose_name='Вторник')),
                ('wednesday', models.BooleanField(default=True, verbose_name='Среда')),
                ('thursday', models.BooleanField(default=True, verbose_name='Четверг')),
                ('friday', models.BooleanField(default=True, verbose_name='Пятница')),
                ('saturday', models.BooleanField(default=True, verbose_name='Суббота')),
                ('sunday', models.BooleanField(default=True, verbose_name='Воскресенье')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('car', models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='taxiapp.car', verbose_name='Автомобиль')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Водитель',
                'verbose_name_plural': 'historical Водители',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalCashbox',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('date', models.DateTimeField(verbose_name='Дата операции')),
                ('slug', models.SlugField(blank=True, max_length=15, verbose_name='Url')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Наличные')),
                ('cash_card', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Карта')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('working_day', models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='taxiapp.working_day')),
            ],
            options={
                'verbose_name': 'historical Движение по кассе',
                'verbose_name_plural': 'historical Движения по кассе',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalCar_cost',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('cost_date', models.DateField(verbose_name='Дата документа')),
                ('cost_num', models.CharField(blank=True, default='', max_length=10, null=True, verbose_name='Номер документа')),
                ('date_of_ex', models.DateField(blank=True, editable=False)),
                ('summ', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Сумма')),
                ('comment', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Комментарий')),
                ('slug', models.SlugField(blank=True, max_length=10, verbose_name='Url')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('car', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='taxiapp.car', verbose_name='Автомобиль')),
                ('cost_item', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='taxiapp.cost_item', verbose_name='Статья затрат')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Расход',
                'verbose_name_plural': 'historical Расходы',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Cashbox',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(verbose_name='Дата операции')),
                ('slug', models.SlugField(blank=True, max_length=15, verbose_name='Url')),
                ('cash', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Наличные')),
                ('cash_card', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Карта')),
                ('working_day', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='taxiapp.working_day')),
            ],
            options={
                'verbose_name': 'Движение по кассе',
                'verbose_name_plural': 'Движения по кассе',
            },
        ),
        migrations.CreateModel(
            name='Car_cost',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cost_date', models.DateField(verbose_name='Дата документа')),
                ('cost_num', models.CharField(blank=True, default='', max_length=10, null=True, verbose_name='Номер документа')),
                ('date_of_ex', models.DateField(auto_now_add=True)),
                ('summ', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Сумма')),
                ('comment', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Комментарий')),
                ('slug', models.SlugField(blank=True, max_length=10, verbose_name='Url')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='taxiapp.car', verbose_name='Автомобиль')),
                ('cost_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='taxiapp.cost_item', verbose_name='Статья затрат')),
            ],
            options={
                'verbose_name': 'Расход',
                'verbose_name_plural': 'Расходы',
            },
        ),
    ]
