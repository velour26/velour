import resend
import os
from django.core.mail.backends.base import BaseEmailBackend


class ResendEmailBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_key = os.environ.get('RESEND_API_KEY', '')
        self._from = os.environ.get('EMAIL_FROM', 'onboarding@resend.dev')

    def send_messages(self, messages):
        if not self._api_key:
            if self.fail_silently:
                return 0
            raise Exception('RESEND_API_KEY not set')

        sent = 0
        for message in messages:
            if self._send(message):
                sent += 1
        return sent

    def _send(self, message):
        try:
            recipients = list(message.to)
            resend.Emails.send({
                'from': message.from_email or self._from,
                'to': recipients,
                'subject': message.subject,
                'html': message.body or '',
            })
            return True
        except Exception as e:
            import logging
            logging.error(f'Resend send error: {e}')
            return False