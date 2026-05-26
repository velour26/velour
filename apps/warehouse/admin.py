from django.contrib import admin
from django.utils.html import format_html
from .models import Warehouse, StockReceipt, StockReceiptItem, StockRevision, StockRevisionItem


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'manager', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address', 'manager__email')


class StockReceiptItemInline(admin.TabularInline):
    model = StockReceiptItem
    extra = 1
    fields = ('product', 'variant', 'quantity', 'unit_price')
    autocomplete_fields = ('product',)


@admin.register(StockReceipt)
class StockReceiptAdmin(admin.ModelAdmin):
    inlines = [StockReceiptItemInline]
    list_display = ('number', 'warehouse', 'status_badge', 'supplier', 'total_items', 'created_by', 'created_at')
    list_filter = ('status', 'warehouse', 'created_at')
    search_fields = ('number', 'supplier', 'created_by__email')
    readonly_fields = ('number', 'created_at', 'updated_at', 'created_by')
    ordering = ('-created_at',)

    fieldsets = (
        ('Приёмка', {'fields': ('number', 'warehouse', 'status', 'supplier')}),
        ('Детали', {'fields': ('note', 'created_by', 'created_at', 'updated_at')}),
    )

    STATUS_COLORS = {
        'draft': '#f39c12',
        'completed': '#27ae60',
        'cancelled': '#e74c3c',
    }

    def status_badge(self, obj):
        color = self.STATUS_COLORS.get(obj.status, '#7f8c8d')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 8px;border-radius:12px;font-size:12px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Статус'

    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Кол-во позиций'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class StockRevisionItemInline(admin.TabularInline):
    model = StockRevisionItem
    extra = 1
    fields = ('product', 'variant', 'expected_quantity', 'actual_quantity', 'discrepancy_display')
    readonly_fields = ('discrepancy_display',)
    autocomplete_fields = ('product',)

    def discrepancy_display(self, obj):
        if obj.pk is None:
            return '-'
        d = obj.discrepancy
        color = '#27ae60' if d == 0 else ('#e74c3c' if d < 0 else '#f39c12')
        return format_html('<span style="color:{};font-weight:bold">{:+d}</span>', color, d)
    discrepancy_display.short_description = 'Расхождение'


@admin.register(StockRevision)
class StockRevisionAdmin(admin.ModelAdmin):
    inlines = [StockRevisionItemInline]
    list_display = ('number', 'warehouse', 'status_badge', 'created_by', 'created_at')
    list_filter = ('status', 'warehouse', 'created_at')
    search_fields = ('number', 'created_by__email')
    readonly_fields = ('number', 'created_at', 'updated_at', 'created_by')
    ordering = ('-created_at',)

    fieldsets = (
        ('Ревизия', {'fields': ('number', 'warehouse', 'status')}),
        ('Детали', {'fields': ('note', 'created_by', 'created_at', 'updated_at')}),
    )

    STATUS_COLORS = {
        'in_progress': '#3498db',
        'completed': '#27ae60',
        'cancelled': '#e74c3c',
    }

    def status_badge(self, obj):
        color = self.STATUS_COLORS.get(obj.status, '#7f8c8d')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 8px;border-radius:12px;font-size:12px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Статус'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
