from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.cart.models import Cart, CartItem
from apps.catalog.models import Product, ProductVariant
from apps.api.serializers.cart import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Слияние гостевой корзины
        if request.session.get('cart_session_key'):
            session_cart = Cart.objects.filter(session_key=request.session['cart_session_key']).first()
            if session_cart:
                for item in session_cart.items.all():
                    existing = cart.items.filter(product=item.product, variant=item.variant).first()
                    if existing:
                        existing.quantity += item.quantity
                        existing.save()
                    else:
                        item.cart = cart
                        item.save()
                session_cart.delete()
            del request.session['cart_session_key']
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=key)
        request.session['cart_session_key'] = key
        return cart


class CartView(APIView):
    permission_classes = []

    def get(self, request):
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)

    def delete(self, request):
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        return Response({'detail': 'Корзина очищена'})


class CartItemAddView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            product = Product.objects.get(pk=data['product_id'], is_active=True)
        except Product.DoesNotExist:
            return Response({'detail': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)

        variant = None
        if data.get('variant_id'):
            variant = ProductVariant.objects.filter(pk=data['variant_id'], product=product).first()

        # Stock check
        qty_requested = data['quantity']
        if variant is not None:
            if variant.stock == 0:
                return Response({'detail': 'Товар закончился'}, status=status.HTTP_400_BAD_REQUEST)
            cart_tmp = get_or_create_cart(request)
            already_in_cart = cart_tmp.items.filter(product=product, variant=variant).values_list('quantity', flat=True).first() or 0
            if already_in_cart + qty_requested > variant.stock:
                return Response(
                    {'detail': f'Доступно только {variant.stock} шт.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        cart = get_or_create_cart(request)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, variant=variant,
            defaults={'quantity': qty_requested}
        )
        if not created:
            if variant and item.quantity + qty_requested > variant.stock:
                return Response(
                    {'detail': f'Доступно только {variant.stock} шт.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            item.quantity += qty_requested
            item.save()

        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)


class CartItemUpdateView(APIView):
    permission_classes = []

    def patch(self, request, item_id):
        cart = get_or_create_cart(request)
        try:
            item = cart.items.get(pk=item_id)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Позиция не найдена'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qty = serializer.validated_data['quantity']

        if qty == 0:
            item.delete()
        else:
            # Проверка остатка при изменении количества
            if item.variant and qty > item.variant.stock:
                return Response(
                    {'detail': f'Доступно только {item.variant.stock} шт.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            item.quantity = qty
            item.save()

        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response(cart_serializer.data)

    def delete(self, request, item_id):
        cart = get_or_create_cart(request)
        cart.items.filter(pk=item_id).delete()
        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response(cart_serializer.data)
