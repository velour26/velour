from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, SubCategory, SubSubCategory,
    FilterGroup, FilterOption,
    Brand, Product, ProductImage, ProductVariant, Review, Favorite
)


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 0
    fields = ('name', 'slug', 'sort_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [SubCategoryInline]
    list_display = ('name', 'slug', 'sort_order', 'is_active', 'product_count')
    list_editable = ('sort_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Товаров'


class SubSubCategoryInline(admin.TabularInline):
    model = SubSubCategory
    extra = 0
    fields = ('name', 'slug', 'sort_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    inlines = [SubSubCategoryInline]
    list_display = ('name', 'category', 'sort_order', 'is_active')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SubSubCategory)
class SubSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'subcategory', 'sort_order', 'is_active')
    list_filter = ('subcategory__category', 'subcategory')


class FilterOptionInline(admin.TabularInline):
    model = FilterOption
    extra = 1
    fields = ('value', 'slug', 'color_code', 'sort_order')
    prepopulated_fields = {'slug': ('value',)}


@admin.register(FilterGroup)
class FilterGroupAdmin(admin.ModelAdmin):
    inlines = [FilterOptionInline]
    list_display = ('name', 'slug', 'filter_type', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    filter_horizontal = ('categories',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ('image', 'alt', 'is_main', 'sort_order', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="60" style="border-radius:4px"/>', obj.image.url)
        return '—'
    image_preview.short_description = 'Превью'


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size', 'color', 'stock', 'sku')
    verbose_name = 'Вариант (размер / цвет / остаток)'
    verbose_name_plural = 'Варианты — здесь настраивается остаток на складе'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductVariantInline]
    list_display = ('article', 'name', 'category', 'price', 'old_price', 'total_stock', 'is_active', 'is_featured', 'is_new', 'main_image_preview')
    list_filter = ('category', 'subcategory', 'is_active', 'is_featured', 'is_new', 'brand')
    search_fields = ('name', 'article', 'description')
    list_editable = ('is_active', 'is_featured', 'is_new', 'price')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('filter_options',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Основное', {'fields': ('name', 'slug', 'article', 'brand', 'description', 'composition')}),
        ('Категория', {'fields': ('category', 'subcategory', 'subsubcategory')}),
        ('Цена', {'fields': ('price', 'old_price')}),
        ('Фильтры', {'fields': ('filter_options',)}),
        ('Флаги', {'fields': ('is_active', 'is_featured', 'is_new')}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    def total_stock(self, obj):
        total = sum(v.stock for v in obj.variants.all())
        color = '#dc3545' if total == 0 else '#28a745' if total > 5 else '#fd7e14'
        return format_html('<span style="color:{};font-weight:600">{}</span>', color, total)
    total_stock.short_description = 'Остаток'

    def main_image_preview(self, obj):
        img = obj.main_image
        if img:
            return format_html('<img src="{}" height="50" style="border-radius:4px"/>', img.image.url)
        return '—'
    main_image_preview.short_description = 'Фото'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved')
    list_editable = ('is_approved',)
    search_fields = ('product__name', 'user__email', 'text')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'product__name')
