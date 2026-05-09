from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from apps.catalog.models import Category, Product, FilterGroup, Brand, Review
from apps.api.serializers.catalog import (
    CategoryListSerializer, CategorySerializer,
    ProductListSerializer, ProductDetailSerializer,
    FilterGroupSerializer, BrandSerializer, ReviewSerializer
)
from apps.api.filters.catalog import ProductFilter


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True).prefetch_related(
        'subcategories__subsubcategories', 'filter_groups__options'
    )
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategorySerializer
        return CategoryListSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related(
        'category', 'subcategory', 'brand'
    ).prefetch_related('images', 'variants__color', 'filter_options__group')
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        ids = self.request.query_params.get('ids', '')
        if ids:
            id_list = [int(x) for x in ids.split(',') if x.strip().isdigit()]
            queryset = queryset.filter(pk__in=id_list)
        search = self.request.query_params.get('search', '').strip()
        if search:
            q = search.lower()
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(name__icontains=search) |
                Q(article__icontains=search) |
                Q(description__icontains=q) |
                Q(description__icontains=search)
            ).distinct()
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        product = self.get_object()
        reviews = product.reviews.filter(is_approved=True).select_related('user')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_review(self, request, slug=None):
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=201)


class FilterGroupListView(generics.ListAPIView):
    serializer_class = FilterGroupSerializer

    def get_queryset(self):
        qs = FilterGroup.objects.filter(is_active=True).prefetch_related('options')
        category_slug = self.request.query_params.get('category')
        if category_slug:
            qs = qs.filter(categories__slug=category_slug)
        return qs


class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
