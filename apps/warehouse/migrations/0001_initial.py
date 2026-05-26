import apps.warehouse.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_store_employee_role'),
        ('catalog', '0003_review_moderation_default'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('address', models.CharField(blank=True, max_length=300, verbose_name='Адрес')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('manager', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='warehouses',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Ответственный менеджер',
                    limit_choices_to={'role': 'manager'},
                )),
            ],
            options={
                'verbose_name': 'Склад',
                'verbose_name_plural': 'Склады',
            },
        ),
        migrations.CreateModel(
            name='StockReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(default=apps.warehouse.models.generate_receipt_number, max_length=20, unique=True, verbose_name='Номер')),
                ('status', models.CharField(choices=[('draft', 'Черновик'), ('completed', 'Завершена'), ('cancelled', 'Отменена')], default='draft', max_length=20, verbose_name='Статус')),
                ('supplier', models.CharField(blank=True, max_length=200, verbose_name='Поставщик')),
                ('note', models.TextField(blank=True, verbose_name='Примечание')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receipts', to='warehouse.warehouse', verbose_name='Склад')),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_receipts',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Создал',
                )),
            ],
            options={
                'verbose_name': 'Приёмка',
                'verbose_name_plural': 'Приёмки',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StockReceiptItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Количество')),
                ('unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Закупочная цена')),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='warehouse.stockreceipt')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.product', verbose_name='Товар')),
                ('variant', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='catalog.productvariant',
                    verbose_name='Вариант',
                )),
            ],
            options={
                'verbose_name': 'Позиция приёмки',
                'verbose_name_plural': 'Позиции приёмки',
            },
        ),
        migrations.CreateModel(
            name='StockRevision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(default=apps.warehouse.models.generate_revision_number, max_length=20, unique=True, verbose_name='Номер')),
                ('status', models.CharField(choices=[('in_progress', 'В процессе'), ('completed', 'Завершена'), ('cancelled', 'Отменена')], default='in_progress', max_length=20, verbose_name='Статус')),
                ('note', models.TextField(blank=True, verbose_name='Примечание')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revisions', to='warehouse.warehouse', verbose_name='Склад')),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_revisions',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Создал',
                )),
            ],
            options={
                'verbose_name': 'Ревизия',
                'verbose_name_plural': 'Ревизии',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StockRevisionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expected_quantity', models.PositiveIntegerField(default=0, verbose_name='Ожидаемое кол-во')),
                ('actual_quantity', models.PositiveIntegerField(default=0, verbose_name='Фактическое кол-во')),
                ('revision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='warehouse.stockrevision')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.product', verbose_name='Товар')),
                ('variant', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='catalog.productvariant',
                    verbose_name='Вариант',
                )),
            ],
            options={
                'verbose_name': 'Позиция ревизии',
                'verbose_name_plural': 'Позиции ревизии',
            },
        ),
    ]
