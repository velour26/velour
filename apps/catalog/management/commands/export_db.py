"""
python manage.py export_db [--images]

Экспортирует данные в seed_data/current_db.json.
Изображения сохраняются как относительные пути + копируются в seed_data/images/.

Если указать --images, реальные файлы изображений копируются из MEDIA_ROOT.
Без флага — только JSON с путями.
"""
import json, os, shutil
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

from apps.catalog.models import (
    Category, SubCategory, SubSubCategory, Brand,
    Product, ProductImage, ProductVariant, FilterGroup, FilterOption,
    Review, Favorite
)
from apps.accounts.models import User, Address
from apps.orders.models import Order, OrderItem, StatusHistory
from apps.cart.models import Cart, CartItem
from apps.pages.models import SiteSettings, Page, PageSection, Banner
from apps.newsletter.models import Subscriber


def _serialize_image(obj, field_name='image'):
    img = getattr(obj, field_name, None)
    if not img:
        return None
    path = img.name if hasattr(img, 'name') else str(img)
    return path


def _serialize_filefield(obj, field_name):
    f = getattr(obj, field_name, None)
    if not f:
        return None
    if callable(f.name):
        return None
    return f.name


def _model_to_dict(instance, fields):
    out = {'pk': instance.pk}
    for f in fields:
        val = getattr(instance, f, None)
        if isinstance(val, (int, float, bool, type(None), str)):
            out[f] = val
        elif hasattr(val, 'pk'):
            out[f] = val.pk
        elif hasattr(val, 'strftime'):
            out[f] = val.isoformat()
        else:
            out[f] = str(val) if val is not None else None
    return out


def _image_to_dict(img):
    return {
        'pk': img.pk,
        'product': img.product_id,
        'image': img.image.name if hasattr(img.image, 'name') else str(img.image),
        'alt': img.alt,
        'is_main': img.is_main,
        'sort_order': img.sort_order,
    }


def _variant_to_dict(v):
    return {
        'pk': v.pk,
        'product': v.product_id,
        'size': v.size,
        'color_id': v.color_id,
        'stock': v.stock,
        'sku': v.sku,
    }


EXPORT_FIELDS = {
    SiteSettings: ['site_name', 'site_description', 'phone', 'email', 'address',
                   'vk_url', 'telegram_url', 'instagram_url', 'delivery_info',
                   'return_policy', 'free_delivery_from'],
    Category: ['name', 'slug', 'description', 'image', 'sort_order', 'is_active'],
    SubCategory: ['category', 'name', 'slug', 'description', 'sort_order', 'is_active'],
    SubSubCategory: ['subcategory', 'name', 'slug', 'sort_order', 'is_active'],
    FilterGroup: ['name', 'slug', 'filter_type', 'sort_order', 'is_active'],
    FilterOption: ['group', 'value', 'slug', 'color_code', 'sort_order'],
    Brand: ['name', 'slug'],
    Product: ['category', 'subcategory', 'subsubcategory', 'brand', 'name', 'slug',
              'article', 'description', 'composition', 'price', 'old_price',
              'is_active', 'is_featured', 'is_new'],
    FilterOption: ['group', 'value', 'slug', 'color_code', 'sort_order'],
    Review: ['product', 'user', 'rating', 'text', 'is_approved'],
    User: ['email', 'username', 'first_name', 'last_name', 'role',
           'phone', 'email_confirmed'],
    Address: ['user', 'label', 'city', 'street', 'apartment', 'postal_code', 'is_default'],
    Order: ['user', 'session_key', 'guest_email', 'guest_name', 'guest_phone',
            'status', 'payment_method', 'payment_status', 'delivery_city',
            'delivery_street', 'delivery_apartment', 'delivery_postal_code',
            'comment', 'promo_code', 'subtotal', 'delivery_cost', 'total'],
    OrderItem: ['order', 'product', 'product_name', 'product_article',
                'variant_id', 'price', 'quantity'],
    StatusHistory: ['order', 'status', 'comment', 'created_by'],
    Cart: ['user', 'session_key'],
    CartItem: ['cart', 'product', 'variant_id', 'quantity'],
    Subscriber: ['email', 'name', 'is_active', 'confirm_token',
                 'is_confirmed', 'subscribed_at', 'unsubscribed_at'],
    Page: ['slug', 'title', 'meta_description', 'is_active'],
    PageSection: ['page', 'key', 'label', 'text', 'image', 'link', 'is_visible', 'sort_order'],
    Banner: ['title', 'subtitle', 'button_text', 'button_link', 'image',
             'sort_order', 'is_active'],
}


class Command(BaseCommand):
    help = 'Export all data to seed_data/current_db.json'

    def add_arguments(self, parser):
        parser.add_argument('--images', action='store_true',
                            help='Also copy image files to seed_data/images/')

    def handle(self, *args, **options):
        copy_images = options['images']
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        out_dir = base_dir / 'seed_data'
        images_dir = out_dir / 'images'
        out_dir.mkdir(exist_ok=True)
        if copy_images:
            images_dir.mkdir(exist_ok=True)

        # Collect all images to copy
        image_files = []

        data = {}

        # SiteSettings
        s = SiteSettings.get()
        data['SiteSettings'] = [_model_to_dict(s, EXPORT_FIELDS[SiteSettings])]
        if copy_images and s.image:
            image_files.append(s.image.name)

        # FilterGroups + FilterOptions
        data['FilterGroup'] = [
            _model_to_dict(g, ['name', 'slug', 'filter_type', 'sort_order', 'is_active'])
            for g in FilterGroup.objects.all()
        ]
        data['FilterOption'] = [
            _model_to_dict(o, ['group', 'value', 'slug', 'color_code', 'sort_order'])
            for o in FilterOption.objects.all()
        ]

        # Categories
        for model in [Category, SubCategory, SubSubCategory, Brand]:
            data[model.__name__] = [
                _model_to_dict(o, EXPORT_FIELDS.get(model, [])) for o in model.objects.all()
            ]
            if copy_images:
                for obj in model.objects.all():
                    if hasattr(obj, 'image') and obj.image:
                        image_files.append(obj.image.name)

        # Products
        data['Product'] = [
            _model_to_dict(p, ['category', 'subcategory', 'subsubcategory', 'brand',
                               'name', 'slug', 'article', 'description', 'composition',
                               'price', 'old_price', 'is_active', 'is_featured', 'is_new'])
            for p in Product.objects.all()
        ]
        data['ProductImage'] = [_image_to_dict(i) for i in ProductImage.objects.all()]
        data['ProductVariant'] = [_variant_to_dict(v) for v in ProductVariant.objects.all()]

        if copy_images:
            for img in ProductImage.objects.all():
                if img.image:
                    image_files.append(img.image.name)

        # Filter options for products
        data['Product_filter_options'] = [
            {'product_id': p.id, 'filteroption_id': fo.id}
            for p in Product.objects.prefetch_related('filter_options')
            for fo in p.filter_options.all()
        ]

        # Reviews
        data['Review'] = [
            _model_to_dict(r, ['product', 'user', 'rating', 'text', 'is_approved'])
            for r in Review.objects.all()
        ]

        # Users (without password hash)
        data['User'] = [
            _model_to_dict(u, ['pk', 'email', 'username', 'first_name', 'last_name',
                               'role', 'phone', 'email_confirmed'])
            for u in User.objects.all()
        ]

        # Addresses
        data['Address'] = [
            _model_to_dict(a, ['user', 'label', 'city', 'street', 'apartment', 'postal_code', 'is_default'])
            for a in Address.objects.all()
        ]

        # Orders
        data['Order'] = [
            _model_to_dict(o, ['user', 'session_key', 'guest_email', 'guest_name', 'guest_phone',
                               'status', 'payment_method', 'payment_status', 'delivery_city',
                               'delivery_street', 'delivery_apartment', 'delivery_postal_code',
                               'comment', 'promo_code', 'subtotal', 'delivery_cost', 'total'])
            for o in Order.objects.all()
        ]
        data['OrderItem'] = [
            _model_to_dict(i, ['order', 'product', 'product_name', 'product_article',
                               'variant_id', 'price', 'quantity'])
            for i in OrderItem.objects.all()
        ]
        data['StatusHistory'] = [
            _model_to_dict(h, ['order', 'status', 'comment', 'created_by'])
            for h in StatusHistory.objects.all()
        ]

        # Carts
        data['Cart'] = [_model_to_dict(c, ['user', 'session_key']) for c in Cart.objects.all()]
        data['CartItem'] = [
            _model_to_dict(i, ['cart', 'product', 'variant_id', 'quantity'])
            for i in CartItem.objects.all()
        ]

        # Pages
        data['Page'] = [
            _model_to_dict(p, ['slug', 'title', 'meta_description', 'is_active'])
            for p in Page.objects.all()
        ]
        data['PageSection'] = [
            _model_to_dict(s, ['page', 'key', 'label', 'text', 'image', 'link', 'is_visible', 'sort_order'])
            for s in PageSection.objects.all()
        ]
        if copy_images:
            for s in PageSection.objects.all():
                if s.image:
                    image_files.append(s.image.name)

        data['Banner'] = [
            _model_to_dict(b, ['title', 'subtitle', 'button_text', 'button_link',
                               'image', 'sort_order', 'is_active'])
            for b in Banner.objects.all()
        ]
        if copy_images:
            for b in Banner.objects.all():
                if b.image:
                    image_files.append(b.image.name)

        # Subscribers
        data['Subscriber'] = [
            _model_to_dict(s, ['email', 'name', 'is_active', 'confirm_token',
                               'is_confirmed', 'subscribed_at', 'unsubscribed_at'])
            for s in Subscriber.objects.all()
        ]

        # Favorites
        data['Favorite'] = [
            {'user_id': f.user_id, 'product_id': f.product_id}
            for f in Favorite.objects.all()
        ]

        # Write JSON
        out_file = out_dir / 'current_db.json'
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.stdout.write(f'  ✓ JSON saved to {out_file}')

        # Copy image files
        if copy_images:
            copied = set()
            media_root = Path(settings.MEDIA_ROOT)
            for img_path in image_files:
                if not img_path or img_path in copied:
                    continue
                src = media_root / img_path
                if src.exists():
                    dst = images_dir / img_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    copied.add(img_path)
                else:
                    self.stdout.write(f'  ⚠ Missing: {img_path}')
            self.stdout.write(f'  ✓ Images copied ({len(copied)} files)')

        # Print summary
        for key, records in data.items():
            self.stdout.write(f'    {key}: {len(records)}')