from rest_framework import serializers
from apps.catalog.models import (
    Category, SubCategory, SubSubCategory,
    FilterGroup, FilterOption, Brand,
    Product, ProductImage, ProductVariant, Review
)


class FilterOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterOption
        fields = ('id', 'value', 'slug', 'color_code', 'sort_order')


class FilterGroupSerializer(serializers.ModelSerializer):
    options = FilterOptionSerializer(many=True, read_only=True)

    class Meta:
        model = FilterGroup
        fields = ('id', 'name', 'slug', 'filter_type', 'options')


class SubSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubSubCategory
        fields = ('id', 'name', 'slug')


class SubCategorySerializer(serializers.ModelSerializer):
    subsubcategories = SubSubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'slug', 'subsubcategories')


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    filter_groups = FilterGroupSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'image', 'subcategories', 'filter_groups')


class CategoryListSerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'image', 'subcategories')


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'slug', 'logo')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt', 'is_main', 'sort_order')


class ProductVariantSerializer(serializers.ModelSerializer):
    color_name = serializers.CharField(source='color.value', read_only=True, allow_null=True)
    color_code = serializers.CharField(source='color.color_code', read_only=True, allow_null=True)

    class Meta:
        model = ProductVariant
        fields = ('id', 'size', 'color', 'color_name', 'color_code', 'stock', 'sku')


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id', 'user', 'user_name', 'rating', 'text', 'created_at')
        read_only_fields = ('user', 'created_at')

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    has_variants = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'article', 'price', 'old_price',
            'discount_percent', 'is_new', 'is_featured',
            'category_name', 'category_slug', 'main_image', 'has_variants'
        )

    def get_has_variants(self, obj):
        # Uses prefetched variants cache if available (no extra query)
        if hasattr(obj, '_prefetched_objects_cache') and 'variants' in obj._prefetched_objects_cache:
            return bool(obj._prefetched_objects_cache['variants'])
        return obj.variants.exists()

    def get_main_image(self, obj):
        img = obj.main_image
        if img:
            request = self.context.get('request')
            url = img.image.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True, source='approved_reviews')
    category = CategoryListSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    filter_options = FilterOptionSerializer(many=True, read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'article', 'description', 'composition',
            'price', 'old_price', 'discount_percent',
            'is_new', 'is_featured', 'is_active',
            'category', 'brand', 'filter_options',
            'images', 'variants', 'reviews', 'avg_rating',
            'created_at',
        )

    def get_avg_rating(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None
