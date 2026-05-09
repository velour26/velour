from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_email(to, subject, html):
    recipients = to if isinstance(to, list) else [to]
    try:
        send_mail(
            subject=subject,
            message='',
            html_message=html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f'Email send failed: {e}')
        return False