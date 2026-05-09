import json
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from .models import Category, Product, FilterGroup, Favorite


class CatalogView(TemplateView):
    template_name = 'catalog/catalog.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.filter(is_active=True).prefetch_related('subcategories')
        ctx['filter_groups'] = FilterGroup.objects.filter(is_active=True).prefetch_related('options')
        ctx['total_count'] = Product.objects.filter(is_active=True).count()
        return ctx


class CategoryView(TemplateView):
    template_name = 'catalog/catalog.html'

    def dispatch(self, request, *args, **kwargs):
        category_slug = kwargs.get('category_slug')
        if (
            category_slug
            and not Category.objects.filter(slug=category_slug, is_active=True).exists()
        ):
            product = Product.objects.filter(
                slug=category_slug, is_active=True
            ).select_related('category').first()
            if product:
                return redirect(
                    'product-detail',
                    category_slug=product.category.slug,
                    product_slug=product.slug,
                    permanent=True,
                )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, category_slug=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        ctx['current_category'] = category
        ctx['categories'] = Category.objects.filter(is_active=True).prefetch_related('subcategories')
        ctx['filter_groups'] = FilterGroup.objects.filter(
            is_active=True
        ).filter(categories=category).prefetch_related('options')
        if not ctx['filter_groups'].exists():
            ctx['filter_groups'] = FilterGroup.objects.filter(is_active=True).prefetch_related('options')
        ctx['total_count'] = Product.objects.filter(is_active=True, category=category).count()
        return ctx


class FavoritesView(TemplateView):
    template_name = 'catalog/favorites.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx['favorites'] = Product.objects.filter(
                favorited_by__user=self.request.user, is_active=True
            ).prefetch_related('images', 'variants').select_related('category')
        else:
            ctx['favorites'] = []
        return ctx


class ProductDetailView(TemplateView):
    template_name = 'catalog/product_detail.html'

    def get_context_data(self, category_slug=None, product_slug=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = get_object_or_404(
            Product.objects.select_related('category', 'brand')
            .prefetch_related('images', 'variants__color', 'filter_options__group', 'reviews__user'),
            slug=product_slug, is_active=True
        )
        ctx['product'] = product
        ctx['related'] = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(pk=product.pk).prefetch_related('images', 'variants').select_related('category')[:4]

        # Pass full variant data as JSON for the JS size/color selector
        variants = list(product.variants.all().select_related('color'))
        ctx['variants_json'] = json.dumps([{
            'id': v.id,
            'size': v.size or '',
            'color_name': v.color.value if v.color else '',
            'color_code': v.color.color_code if v.color else '',
            'stock': v.stock,
        } for v in variants])
        return ctx
