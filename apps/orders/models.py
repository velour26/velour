from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string


def generate_order_number():
    return f'ORD-{get_random_string(8).upper()}'


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает подтверждения'
        CONFIRMED = 'confirmed', 'Подтверждён'
        PAID = 'paid', 'Оплачен'
        ASSEMBLING = 'assembling', 'Сборка'
        SHIPPED = 'shipped', 'Отправлен'
        DELIVERED = 'delivered', 'Доставлен'
        CANCELLED = 'cancelled', 'Отменён'
        RETURNED = 'returned', 'Возврат'

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'При получении'
        SBP = 'sbp', 'СБП'
        CARD = 'card', 'Банковская карта'

    number = models.CharField(max_length=20, unique=True, default=generate_order_number)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='orders')
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    store = models.ForeignKey(
        'accounts.Store', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name='Магазин (заказ от сотрудника)',
    )
    # Гость (если без аккаунта)
    guest_email = models.EmailField(blank=True)
    guest_name = models.CharField(max_length=100, blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Ожидает'), ('paid', 'Оплачен'), ('failed', 'Ошибка'), ('refunded', 'Возврат')],
        default='pending'
    )

    # Адрес доставки (снимок на момент заказа)
    delivery_city = models.CharField(max_length=100)
    delivery_street = models.CharField(max_length=200)
    delivery_apartment = models.CharField(max_length=50, blank=True)
    delivery_postal_code = models.CharField(max_length=20)

    comment = models.TextField(blank=True)
    promo_code = models.CharField(max_length=50, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ {self.number}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey('catalog.ProductVariant', on_delete=models.SET_NULL,
                                null=True, blank=True, verbose_name='Вариант')
    product_name = models.CharField(max_length=255)
    product_article = models.CharField(max_length=50)
    variant_info = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product_name} x{self.quantity}'

    @property
    def subtotal(self):
        if self.price is None or self.quantity is None:
            return 0
        return self.price * self.quantity


class StatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.Status.choices)
    comment = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'История статусов'
        verbose_name_plural = 'История статусов'
        ordering = ['created_at']
