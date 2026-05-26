import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_store_employee_role'),
        ('orders', '0003_order_session_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='store',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='orders',
                to='accounts.store',
                verbose_name='Магазин (заказ от сотрудника)',
            ),
        ),
    ]
