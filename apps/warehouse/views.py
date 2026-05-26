from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from apps.accounts.views import ManagerRequiredMixin
from .models import Warehouse, StockReceipt, StockRevision


class WarehouseListView(ManagerRequiredMixin, TemplateView):
    template_name = 'manager/warehouse.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['warehouses'] = Warehouse.objects.filter(is_active=True).select_related('manager')
        ctx['recent_receipts'] = StockReceipt.objects.select_related('warehouse', 'created_by').order_by('-created_at')[:10]
        ctx['recent_revisions'] = StockRevision.objects.select_related('warehouse', 'created_by').order_by('-created_at')[:10]
        return ctx


class ReceiptListView(ManagerRequiredMixin, TemplateView):
    template_name = 'manager/receipts.html'

    def get_context_data(self, warehouse_pk=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['warehouse'] = get_object_or_404(Warehouse, pk=warehouse_pk, is_active=True)
        ctx['receipts'] = StockReceipt.objects.filter(warehouse_id=warehouse_pk).select_related('created_by').prefetch_related('items__product').order_by('-created_at')
        return ctx


class RevisionListView(ManagerRequiredMixin, TemplateView):
    template_name = 'manager/revisions.html'

    def get_context_data(self, warehouse_pk=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['warehouse'] = get_object_or_404(Warehouse, pk=warehouse_pk, is_active=True)
        ctx['revisions'] = StockRevision.objects.filter(warehouse_id=warehouse_pk).select_related('created_by').prefetch_related('items__product').order_by('-created_at')
        return ctx
