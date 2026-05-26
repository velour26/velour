from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from apps.accounts.views import ManagerRequiredMixin
from .models import Order


class CheckoutView(TemplateView):
    template_name = 'orders/checkout.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            ctx['addresses'] = user.addresses.all()
            if user.is_employee:
                ctx['employee_stores'] = user.assigned_stores.filter(is_active=True)
        return ctx


class ManagerDashboardView(ManagerRequiredMixin, TemplateView):
    template_name = 'manager/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = Order.objects.filter(store__isnull=False).select_related('store', 'user').prefetch_related('items')
        ctx['store_orders'] = qs.order_by('-created_at')[:50]
        ctx['store_orders_count'] = qs.count()
        ctx['pending_count'] = qs.filter(status='pending').count()
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