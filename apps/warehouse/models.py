from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string


def generate_receipt_number():
    return f'REC-{get_random_string(8).upper()}'


def generate_revision_number():
    return f'REV-{get_random_string(8).upper()}'


class Warehouse(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    address = models.CharField(max_length=300, blank=True, verbose_name='Адрес')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='warehouses', verbose_name='Ответственный менеджер',
        limit_choices_to={'role': 'manager'},
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'

    def __str__(self):
        return self.name


class StockReceipt(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        COMPLETED = 'completed', 'Завершена'
        CANCELLED = 'cancelled', 'Отменена'

    number = models.CharField(max_length=20, unique=True, default=generate_receipt_number, verbose_name='Номер')
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name='receipts', verbose_name='Склад',
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name='Статус')
    supplier = models.CharField(max_length=200, blank=True, verbose_name='Поставщик')
    note = models.TextField(blank=True, verbose_name='Примечание')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_receipts', verbose_name='Создал',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Приёмка'
        verbose_name_plural = 'Приёмки'
        ordering = ['-created_at']

    def __str__(self):
        return f'Приёмка {self.number}'

    @property
    def total_items(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0


class StockReceiptItem(models.Model):
    receipt = models.ForeignKey(StockReceipt, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'catalog.Product', on_delete=models.CASCADE, verbose_name='Товар',
    )
    variant = models.ForeignKey(
        'catalog.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Вариант',
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Закупочная цена')

    class Meta:
        verbose_name = 'Позиция приёмки'
        verbose_name_plural = 'Позиции приёмки'

    def __str__(self):
        return f'{self.product} x{self.quantity}'

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


class StockRevision(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'В процессе'
        COMPLETED = 'completed', 'Завершена'
        CANCELLED = 'cancelled', 'Отменена'

    number = models.CharField(max_length=20, unique=True, default=generate_revision_number, verbose_name='Номер')
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name='revisions', verbose_name='Склад',
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS, verbose_name='Статус')
    note = models.TextField(blank=True, verbose_name='Примечание')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_revisions', verbose_name='Создал',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ревизия'
        verbose_name_plural = 'Ревизии'
        ordering = ['-created_at']

    def __str__(self):
        return f'Ревизия {self.number}'


class StockRevisionItem(models.Model):
    revision = models.ForeignKey(StockRevision, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'catalog.Product', on_delete=models.CASCADE, verbose_name='Товар',
    )
    variant = models.ForeignKey(
        'catalog.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Вариант',
    )
    expected_quantity = models.PositiveIntegerField(default=0, verbose_name='Ожидаемое кол-во')
    actual_quantity = models.PositiveIntegerField(default=0, verbose_name='Фактическое кол-во')

    class Meta:
        verbose_name = 'Позиция ревизии'
        verbose_name_plural = 'Позиции ревизии'

    def __str__(self):
        return f'{self.product}'

    @property
    def discrepancy(self):
        return self.actual_quantity - self.expected_quantity
