from rest_framework import serializers
from apps.orders.models import Order, OrderItem, StatusHistory
from apps.accounts.models import Address


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_article', 'variant_info', 'price', 'quantity', 'subtotal')


class StatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusHistory
        fields = ('status', 'comment', 'created_at')


class OrderListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'number', 'status', 'status_display', 'payment_method', 'payment_display',
                  'total', 'items_count', 'created_at')

    def get_items_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = StatusHistorySerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'number', 'status', 'status_display',
            'payment_method', 'payment_display', 'payment_status',
            'guest_name', 'guest_email', 'guest_phone',
            'delivery_city', 'delivery_street', 'delivery_apartment', 'delivery_postal_code',
            'comment', 'subtotal', 'delivery_cost', 'discount_amount', 'total',
            'items', 'status_history', 'created_at',
        )


class CreateOrderSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=Order.PaymentMethod.choices)
    delivery_city = serializers.CharField(max_length=100)
    delivery_street = serializers.CharField(max_length=200)
    delivery_apartment = serializers.CharField(max_length=50, required=False, allow_blank=True)
    delivery_postal_code = serializers.CharField(max_length=20)
    comment = serializers.CharField(required=False, allow_blank=True)
    guest_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    guest_email = serializers.EmailField(required=False, allow_blank=True)
    guest_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    # Создание аккаунта при заказе
    create_account = serializers.BooleanField(required=False, default=False)
    account_password = serializers.CharField(required=False, allow_blank=True, write_only=True)
    use_address_id = serializers.IntegerField(required=False, allow_null=True)
