from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from django.contrib.auth import login
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings as django_settings
from apps.orders.models import Order, OrderItem, StatusHistory
from apps.cart.models import Cart, CartItem
from apps.accounts.models import User
from apps.api.serializers.orders import (
    CreateOrderSerializer, OrderListSerializer, OrderDetailSerializer
)
from apps.api.views.cart import get_or_create_cart
import threading
import logging

logger = logging.getLogger(__name__)


class CreateOrderView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cart = get_or_create_cart(request)
        if not cart.items.exists():
            return Response({'detail': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

        # Создание аккаунта при заказе
        user = request.user if request.user.is_authenticated else None
        if not user and data.get('create_account') and data.get('guest_email') and data.get('account_password'):
            if not User.objects.filter(email=data['guest_email']).exists():
                user = User.objects.create_user(
                    email=data['guest_email'],
                    username=data['guest_email'],
                    password=data['account_password'],
                    first_name=data.get('guest_name', '').split()[0] if data.get('guest_name') else '',
                )
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # Суммы
        items = list(cart.items.select_related('product', 'variant__color'))
        subtotal = sum(i.subtotal for i in items)
        delivery_cost = 0 if subtotal >= django_settings.JAZZMIN_SETTINGS.get('free_delivery_from', 5000) else 300
        try:
            from apps.pages.models import SiteSettings
            site = SiteSettings.get()
            free_from = site.free_delivery_from
            delivery_cost = 0 if subtotal >= free_from else 300
        except Exception:
            pass
        total = subtotal + delivery_cost

        # Адрес доставки
        address_data = {}
        if data.get('use_address_id') and user:
            addr = user.addresses.filter(pk=data['use_address_id']).first()
            if addr:
                address_data = {
                    'delivery_city': addr.city,
                    'delivery_street': addr.street,
                    'delivery_apartment': addr.apartment,
                    'delivery_postal_code': addr.postal_code,
                }
        if not address_data:
            address_data = {
                'delivery_city': data['delivery_city'],
                'delivery_street': data['delivery_street'],
                'delivery_apartment': data.get('delivery_apartment', ''),
                'delivery_postal_code': data['delivery_postal_code'],
            }

        order = Order.objects.create(
            user=user,
            guest_email=data.get('guest_email', ''),
            guest_name=data.get('guest_name', ''),
            guest_phone=data.get('guest_phone', ''),
            payment_method=data['payment_method'],
            comment=data.get('comment', ''),
            subtotal=subtotal,
            delivery_cost=delivery_cost,
            total=total,
            **address_data,
        )

        StatusHistory.objects.create(order=order, status=Order.Status.PENDING)

        for item in items:
            variant_parts = []
            if item.variant:
                if item.variant.size:
                    variant_parts.append(f'р. {item.variant.size}')
                if item.variant.color:
                    variant_parts.append(item.variant.color.value)
            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                product_name=item.product.name,
                product_article=item.product.article,
                variant_info=', '.join(variant_parts),
                price=item.product.price,
                quantity=item.quantity,
            )
            # Уменьшаем остаток на складе
            if item.variant:
                item.variant.stock = max(0, item.variant.stock - item.quantity)
                item.variant.save(update_fields=['stock'])

        cart.items.all().delete()

        email_addr = order.user.email if order.user else order.guest_email

        def send_order_email():
            try:
                html = render_to_string('email/order_confirm.html', {'order': order})
                send_mail(
                    subject=f'Заказ {order.number} подтверждён',
                    message=f'Ваш заказ {order.number} принят.',
                    html_message=html,
                    from_email=django_settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email_addr],
                    fail_silently=False,
                )
                logger.info(f'Order confirm email sent to {email_addr} for order {order.number}')
            except Exception as e:
                logger.error(f'Failed to send order email to {email_addr}: {e}', exc_info=True)
        if email_addr:
            threading.Thread(target=send_order_email).start()

        return Response({'order_number': order.number, 'order_id': order.pk}, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'number'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items', 'status_history')


class OrderCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, number):
        order = Order.objects.filter(number=number, user=request.user).first()
        if not order:
            return Response({'detail': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)
        if order.status not in (Order.Status.PENDING, Order.Status.CONFIRMED):
            return Response({'detail': 'Нельзя отменить заказ на этом этапе'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = Order.Status.CANCELLED
        order.save()
        StatusHistory.objects.create(order=order, status=Order.Status.CANCELLED,
                                     comment='Отменён пользователем', created_by=request.user)
        return Response({'detail': 'Заказ отменён'})
