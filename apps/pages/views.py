from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Page, Banner, SiteSettings
from apps.catalog.models import Product, Category


class HomeView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['banners'] = Banner.objects.filter(is_active=True)
        ctx['featured_products'] = Product.objects.filter(
            is_active=True, is_featured=True
        ).prefetch_related('images', 'variants').select_related('category')[:8]
        ctx['new_products'] = Product.objects.filter(
            is_active=True, is_new=True
        ).prefetch_related('images', 'variants').select_related('category')[:8]
        category_fallbacks = [
            'categories/female.jpg',
            'categories/male.jpg',
            'categories/acs.jpg',
        ]
        categories = list(Category.objects.filter(is_active=True).order_by('sort_order', 'name'))
        for index, category in enumerate(categories):
            if category.image:
                category.home_image_url = category.image.url
            elif index < len(category_fallbacks):
                category.home_image_url = f'{settings.MEDIA_URL}{category_fallbacks[index]}'
            else:
                category.home_image_url = ''
        ctx['categories'] = categories
        try:
            home_page = Page.objects.prefetch_related('sections').get(slug='home')
            ctx['sections'] = {s.key: s for s in home_page.sections.filter(is_visible=True)}
        except Page.DoesNotExist:
            ctx['sections'] = {}
        return ctx


class PageView(TemplateView):
    template_name = 'pages/page.html'

    def get_context_data(self, slug=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = get_object_or_404(Page, slug=slug, is_active=True)
        ctx['page'] = page
        ctx['sections'] = {s.key: s for s in page.sections.filter(is_visible=True)}
        return ctx
