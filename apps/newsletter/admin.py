from django.contrib import admin
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Subscriber, Newsletter
import threading


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'is_confirmed', 'subscribed_at')
    list_filter = ('is_active', 'is_confirmed')
    search_fields = ('email', 'name')
    actions = ['deactivate_selected']

    def deactivate_selected(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_selected.short_description = 'Деактивировать выбранных'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'status', 'recipients_count', 'sent_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('subject',)
    readonly_fields = ('sent_at', 'recipients_count')
    actions = ['send_newsletter']

    def send_newsletter(self, request, queryset):
        for newsletter in queryset.filter(status=Newsletter.Status.DRAFT):
            recipients = list(
                Subscriber.objects.filter(is_active=True).values_list('email', flat=True)
            )
            if recipients:
                def send():
                    send_mail(
                        subject=newsletter.subject,
                        message=newsletter.body_text or '',
                        html_message=newsletter.body_html,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=recipients,
                        fail_silently=True,
                    )
                threading.Thread(target=send).start()
                newsletter.status = Newsletter.Status.SENT
                newsletter.sent_at = timezone.now()
                newsletter.recipients_count = len(recipients)
                newsletter.save()
        self.message_user(request, 'Рассылка отправлена')
    send_newsletter.short_description = 'Отправить рассылку'
