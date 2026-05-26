from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, StatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_article', 'variant_info', 'variant', 'price', 'quantity', 'subtotal')
    fields = ('product_name', 'variant_info', 'price', 'quantity', 'subtotal')

    def subtotal(self, obj):
        return f'{obj.subtotal:.2f} ₽'
    subtotal.short_description = 'Сумма'


class StatusHistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ('status', 'comment', 'created_by', 'created_at')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline, StatusHistoryInline]
    list_display = ('number', 'customer_info', 'store_badge', 'status_badge', 'payment_method', 'total_display', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'store', 'created_at')
    search_fields = ('number', 'user__email', 'guest_email', 'guest_name', 'store__name')
    readonly_fields = ('number', 'created_at', 'updated_at', 'subtotal', 'total')
    ordering = ('-created_at',)

    fieldsets = (
        ('Заказ', {'fields': ('number', 'status', 'payment_method', 'payment_status')}),
        ('Клиент / Магазин', {'fields': ('user', 'store', 'guest_name', 'guest_email', 'guest_phone')}),
        ('Доставка', {'fields': ('delivery_city', 'delivery_street', 'delivery_apartment', 'delivery_postal_code')}),
        ('Суммы', {'fields': ('subtotal', 'delivery_cost', 'discount_amount', 'total')}),
        ('Прочее', {'fields': ('comment', 'promo_code', 'created_at', 'updated_at')}),
    )

    def customer_info(self, obj):
        if obj.user:
            return obj.user.email
        return obj.guest_email or obj.guest_name
    customer_info.short_description = 'Клиент'

    def store_badge(self, obj):
        if obj.store:
            return format_html(
                '<span style="background:#8e44ad;color:#fff;padding:3px 8px;border-radius:12px;font-size:12px">{}</span>',
                obj.store.name
            )
        return '-'
    store_badge.short_description = 'Магазин'

    STATUS_COLORS = {
        'pending': '#f39c12', 'confirmed': '#3498db', 'paid': '#27ae60',
        'assembling': '#9b59b6', 'shipped': '#2980b9', 'delivered': '#27ae60',
        'cancelled': '#e74c3c', 'returned': '#95a5a6',
    }

    def status_badge(self, obj):
        color = self.STATUS_COLORS.get(obj.status, '#7f8c8d')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 8px;border-radius:12px;font-size:12px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Статус'

    def total_display(self, obj):
        return f'{obj.total:.2f} ₽'
    total_display.short_description = 'Сумма'

    def save_model(self, request, obj, form, change):
        if change:
            old = Order.objects.get(pk=obj.pk)
            if old.status != obj.status:
                StatusHistory.objects.create(
                    order=obj, status=obj.status, created_by=request.user,
                    comment=f'Статус изменён через админ-панель'
                )
        super().save_model(request, obj, form, change)
