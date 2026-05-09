from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.cache import cache
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


class GuestFavoritesSyncView(APIView):
    permission_classes = [AllowAny]

    def _cache_key(self, request):
        return f'guest_fav:{request.session.session_key}'

    def get(self, request):
        key = self._cache_key(request)
        ids = cache.get(key, [])
        return Response({'ids': ids})

    def post(self, request):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            return Response({'error': 'ids must be a list'}, status=400)
        valid_ids = [id for id in ids if isinstance(id, int)]
        key = self._cache_key(request)
        cache.set(key, valid_ids, timeout=86400 * 30)
        return Response({'ids': valid_ids})
