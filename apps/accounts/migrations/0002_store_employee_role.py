from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('customer', 'Покупатель'),
                    ('employee', 'Сотрудник магазина'),
                    ('manager', 'Менеджер'),
                    ('admin', 'Администратор'),
                ],
                default='customer',
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('address', models.CharField(max_length=300, verbose_name='Адрес')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('manager', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='managed_stores',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Менеджер',
                    limit_choices_to={'role': 'manager'},
                )),
                ('employees', models.ManyToManyField(
                    blank=True,
                    related_name='assigned_stores',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Сотрудники',
                    limit_choices_to={'role': 'employee'},
                )),
            ],
            options={
                'verbose_name': 'Магазин',
                'verbose_name_plural': 'Магазины',
            },
        ),
    ]
