from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'subtotal')

    def subtotal(self, obj):
        return f'{obj.subtotal:.2f} ₽'
    subtotal.short_description = 'Сумма'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('__str__', 'item_count', 'total_display', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Позиций'

    def total_display(self, obj):
        return f'{obj.total:.2f} ₽'
    total_display.short_description = 'Сумма'
