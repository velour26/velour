from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from django.conf import settings
from apps.newsletter.models import Subscriber
from apps.api.utils.email import send_email
import threading
import logging

logger = logging.getLogger(__name__)


class SubscribeView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        name = request.data.get('name', '').strip()
        if not email:
            return Response({'detail': 'Email обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        sub, created = Subscriber.objects.get_or_create(
            email=email,
            defaults={'name': name, 'is_active': True, 'is_confirmed': True}
        )
        if not created:
            if not sub.is_active:
                sub.is_active = True
                sub.is_confirmed = True
                sub.save(update_fields=['is_active', 'is_confirmed'])
            else:
                return Response({'detail': 'Вы уже подписаны на рассылку'})

        def send_welcome():
            try:
                html = render_to_string('email/welcome.html', {'name': name or email})
                ok = send_email(email, 'Добро пожаловать в VELOUR!', html)
                logger.info(f'Welcome email to {email}: {"ok" if ok else "failed"}')
            except Exception as e:
                logger.error(f'Failed to send welcome email to {email}: {e}')

        threading.Thread(target=send_welcome).start()
        return Response({'detail': 'Вы подписаны на рассылку!'}, status=201)


class ConfirmSubscriptionView(APIView):
    permission_classes = []

    def get(self, request, token):
        sub = Subscriber.objects.filter(confirm_token=token).first()
        if not sub:
            return Response({'detail': 'Неверный токен'}, status=400)
        sub.is_confirmed = True
        sub.confirm_token = ''
        sub.save(update_fields=['is_confirmed', 'confirm_token'])
        return Response({'detail': 'Подписка подтверждена'})


class UnsubscribeView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        Subscriber.objects.filter(email=email).update(is_active=False)
        return Response({'detail': 'Вы отписались от рассылки'})