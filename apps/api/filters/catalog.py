import django_filters
from apps.catalog.models import Product, FilterOption


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug')
    subcategory = django_filters.CharFilter(field_name='subcategory__slug')
    subsubcategory = django_filters.CharFilter(field_name='subsubcategory__slug')
    brand = django_filters.CharFilter(field_name='brand__slug')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    is_new = django_filters.BooleanFilter()
    is_featured = django_filters.BooleanFilter()
    has_discount = django_filters.BooleanFilter(method='filter_has_discount')
    # Фильтры по опциям (через запятую: ?options=42,17)
    options = django_filters.BaseInFilter(field_name='filter_options__id', lookup_expr='in')

    def filter_has_discount(self, queryset, name, value):
        if value:
            return queryset.filter(old_price__isnull=False)
        return queryset.filter(old_price__isnull=True)

    class Meta:
        model = Product
        fields = ['category', 'subcategory', 'subsubcategory', 'brand',
                  'price_min', 'price_max', 'is_new', 'is_featured', 'has_discount', 'options']
