import resend
import os


def send_email(to, subject, html):
    api_key = os.environ.get('RESEND_API_KEY', '')
    email_from = os.environ.get('EMAIL_FROM', 'VELOUR <velour@resend.dev>')
    if not api_key:
        return False
    try:
        recipients = to if isinstance(to, list) else [to]
        resend.Emails.send({
            'from': email_from,
            'to': recipients,
            'subject': subject,
            'html': html,
        })
        return True
    except Exception as e:
        import logging
        logging.error(f'Resend error: {e}')
        return False