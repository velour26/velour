from django.db import models
from django.utils.crypto import get_random_string


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    confirm_token = models.CharField(max_length=64, blank=True)
    is_confirmed = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return self.email

    def generate_token(self):
        self.confirm_token = get_random_string(64)
        self.save(update_fields=['confirm_token'])
        return self.confirm_token


class Newsletter(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        SENT = 'sent', 'Отправлена'

    subject = models.CharField(max_length=200, verbose_name='Тема письма')
    body_html = models.TextField(verbose_name='HTML содержимое')
    body_text = models.TextField(blank=True, verbose_name='Текстовое содержимое')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    sent_at = models.DateTimeField(null=True, blank=True)
    recipients_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-created_at']

    def __str__(self):
        return self.subject
