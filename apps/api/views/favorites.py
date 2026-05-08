from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.catalog.models import Product, Favorite
from apps.api.serializers.catalog import ProductListSerializer


class FavoriteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.filter(
            favorited_by__user=request.user, is_active=True
        ).select_related('category').prefetch_related('images')
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class FavoriteToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
        if not created:
            fav.delete()
            return Response({'is_favorite': False})
        return Response({'is_favorite': True}, status=status.HTTP_201_CREATED)


class FavoriteStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ids = list(
            Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        )
        return Response({'favorite_ids': ids})
