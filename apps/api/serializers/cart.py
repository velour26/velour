from rest_framework import serializers
from apps.cart.models import Cart, CartItem
from .catalog import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    variant_info = serializers.SerializerMethodField()
    variant_stock = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'variant_id', 'variant_info',
                  'variant_stock', 'quantity', 'subtotal', 'added_at')

    def get_variant_info(self, obj):
        if obj.variant:
            parts = []
            if obj.variant.size:
                parts.append(f'р. {obj.variant.size}')
            if obj.variant.color:
                parts.append(obj.variant.color.value)
            return ', '.join(parts)
        return None

    def get_variant_stock(self, obj):
        if obj.variant:
            return obj.variant.stock
        return None  # нет варианта — лимита нет


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'count')


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)
