from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .models import Order


class CheckoutView(TemplateView):
    template_name = 'orders/checkout.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx['addresses'] = self.request.user.addresses.all()
        return ctx


class PaymentView(TemplateView):
    template_name = 'orders/payment.html'

    def get_context_data(self, order_number=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = Order.objects.filter(number=order_number)
        if self.request.user.is_authenticated:
            qs = qs.filter(user=self.request.user)
        else:
            sk = self.request.session.session_key
            if sk:
                qs = qs.filter(session_key=sk)
            if not qs.exists():
                qs = Order.objects.filter(number=order_number, user__isnull=True)
        ctx['order'] = get_object_or_404(qs)
        return ctx


class OrderSuccessView(TemplateView):
    template_name = 'orders/success.html'

    def get_context_data(self, order_number=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['order_number'] = order_number
        return ctx


class SBPSuccessView(TemplateView):
    template_name = 'orders/sbp_success.html'

    def get(self, request, order_number=None, **kwargs):
        qs = Order.objects.filter(number=order_number)
        if request.user.is_authenticated:
            qs = qs.filter(user=request.user)
        else:
            sk = request.session.session_key
            if sk:
                qs = qs.filter(session_key=sk)
            if not qs.exists():
                qs = Order.objects.filter(number=order_number, user__isnull=True)
        order = get_object_or_404(qs)
        if order.payment_status != 'paid':
            order.payment_status = 'paid'
            order.status = Order.Status.PAID
            order.save(update_fields=['payment_status', 'status'])
        ctx = self.get_context_data(order_number=order_number)
        return self.render_to_response(ctx)


class MyOrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/my_orders.html'


class OrderDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/order_detail.html'

    def get_context_data(self, number=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['order_number'] = number
        return ctx