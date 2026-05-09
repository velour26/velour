"""
python manage.py import_db [--images]

Импортирует данные из seed_data/current_db.json.
Если указать --images, изображения копируются из seed_data/images/ в MEDIA_ROOT.

Порядок загрузки: models без зависимостей → FK/M2M → images.
Пароли пользователей НЕ импортируются (сбрасываются в Admin123!).
"""
import json, os, shutil
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection

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


class Command(BaseCommand):
    help = 'Import data from seed_data/current_db.json'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Clear existing data first')
        parser.add_argument('--images', action='store_true',
                            help='Also restore image files from seed_data/images/')

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent

        import_trigger = os.environ.get('RUN_IMPORT', '').lower()
        if import_trigger not in ('true', '1'):
            self.stdout.write(self.style.WARNING('  ⏭  RUN_IMPORT is not set, skipping import.'))
            self.stdout.write('  Set RUN_IMPORT=true to trigger import (auto-skips next deploy).')
            return

        json_file = base_dir / 'seed_data' / 'current_db.json'
        if not json_file.exists():
            self.stderr.write(f'File not found: {json_file}')
            return

        with open(json_file, encoding='utf-8') as f:
            data = json.load(f)

        if options['flush']:
            self.stdout.write('  flushing existing data...')
            self._flush()

        if options['images']:
            self.stdout.write('  restoring images...')
            src_dir = base_dir / 'seed_data' / 'images'
            dst_dir = Path(settings.MEDIA_ROOT)
            if src_dir.exists():
                for src in src_dir.rglob('*'):
                    if src.is_file():
                        rel = src.relative_to(src_dir)
                        dst = dst_dir / rel
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)
            self.stdout.write('  ✓ Images restored')

        self.stdout.write(self.style.MIGRATE_HEADING('\n📥  Importing VELOUR data\n'))

        # 1. SiteSettings
        if 'SiteSettings' in data and data['SiteSettings']:
            s_data = data['SiteSettings'][0]
            s, _ = SiteSettings.objects.get_or_create(pk=1)
            for k, v in s_data.items():
                if k == 'pk':
                    continue
                setattr(s, k, v)
            s.save()
            self.stdout.write('  ✓ SiteSettings')

        # 2. FilterGroups + FilterOptions
        created_ids = {}  # model_class → {old_pk: new_pk}

        FilterGroup.objects.all().delete()
        FilterOption.objects.all().delete()
        filter_map = {}
        for g_data in data.get('FilterGroup', []):
            g = FilterGroup.objects.create(
                name=g_data['name'], slug=g_data['slug'],
                filter_type=g_data.get('filter_type', 'checkbox'),
                sort_order=g_data.get('sort_order', 0),
                is_active=g_data.get('is_active', True),
            )
            filter_map[g_data['pk']] = g.pk

        FilterOption.objects.all().delete()
        option_map = {}
        for o_data in data.get('FilterOption', []):
            o = FilterOption.objects.create(
                group_id=filter_map[o_data['group']],
                value=o_data['value'], slug=o_data['slug'],
                color_code=o_data.get('color_code', ''),
                sort_order=o_data.get('sort_order', 0),
            )
            option_map[o_data['pk']] = o.pk
        self.stdout.write(f'  ✓ FilterGroups ({len(filter_map)}) + FilterOptions ({len(option_map)})')

        # 3. Categories
        for model in [Category, SubCategory, SubSubCategory, Brand]:
            model.objects.all().delete()
            created_ids[model] = {}

        cat_map, subcat_map, subsubcat_map = {}, {}, {}

        for c_data in data.get('Category', []):
            c = Category.objects.create(
                name=c_data['name'], slug=c_data['slug'],
                description=c_data.get('description', ''),
                image=c_data.get('image', ''),
                sort_order=c_data.get('sort_order', 0),
                is_active=c_data.get('is_active', True),
            )
            cat_map[c_data['pk']] = c.pk

        for sc_data in data.get('SubCategory', []):
            sc = SubCategory.objects.create(
                category_id=cat_map[sc_data['category']],
                name=sc_data['name'], slug=sc_data['slug'],
                description=sc_data.get('description', ''),
                sort_order=sc_data.get('sort_order', 0),
                is_active=sc_data.get('is_active', True),
            )
            subcat_map[sc_data['pk']] = sc.pk

        for ssc_data in data.get('SubSubCategory', []):
            ssc = SubSubCategory.objects.create(
                subcategory_id=subcat_map[ssc_data['subcategory']],
                name=ssc_data['name'], slug=ssc_data['slug'],
                sort_order=ssc_data.get('sort_order', 0),
                is_active=ssc_data.get('is_active', True),
            )
            subsubcat_map[ssc_data['pk']] = ssc.pk

        brand_map = {}
        for b_data in data.get('Brand', []):
            b = Brand.objects.create(name=b_data['name'], slug=b_data['slug'])
            brand_map[b_data['pk']] = b.pk
        self.stdout.write(f'  ✓ Categories + Brands ({len(brand_map)})')

        # 4. Products
        Product.objects.all().delete()
        product_map = {}

        for p_data in data.get('Product', []):
            p = Product.objects.create(
                category_id=cat_map.get(p_data['category']),
                subcategory_id=subcat_map.get(p_data.get('subcategory')),
                subsubcategory_id=subsubcat_map.get(p_data.get('subsubcategory')),
                brand_id=brand_map.get(p_data.get('brand')),
                name=p_data['name'], slug=p_data['slug'],
                article=p_data['article'],
                description=p_data.get('description', ''),
                composition=p_data.get('composition', ''),
                price=p_data['price'],
                old_price=p_data.get('old_price'),
                is_active=p_data.get('is_active', True),
                is_featured=p_data.get('is_featured', False),
                is_new=p_data.get('is_new', False),
            )
            product_map[p_data['pk']] = p.pk
        self.stdout.write(f'  ✓ Products ({len(product_map)})')

        # 5. ProductImages (set image field as path string, not File)
        ProductImage.objects.all().delete()
        for img_data in data.get('ProductImage', []):
            image_path = img_data.get('image', '')
            ProductImage.objects.create(
                product_id=product_map[img_data['product']],
                image=image_path,  # path as string, not file object
                alt=img_data.get('alt', ''),
                is_main=img_data.get('is_main', False),
                sort_order=img_data.get('sort_order', 0),
            )

        # 6. ProductVariants
        ProductVariant.objects.all().delete()
        variant_map = {}
        for v_data in data.get('ProductVariant', []):
            v = ProductVariant.objects.create(
                product_id=product_map[v_data['product']],
                size=v_data.get('size', ''),
                color_id=option_map.get(v_data.get('color_id')) if v_data.get('color_id') else None,
                stock=v_data.get('stock', 0),
                sku=v_data.get('sku', ''),
            )
            variant_map[v_data['pk']] = v.pk
        self.stdout.write(f'  ✓ ProductVariants ({len(variant_map)})')

        # 7. Product filter_options (M2M)
        for pf_data in data.get('Product_filter_options', []):
            p_id = product_map.get(pf_data.get('product_id'))
            fo_id = option_map.get(pf_data.get('filteroption_id'))
            if p_id and fo_id:
                Product.objects.filter(pk=p_id).first().filter_options.add(fo_id)
        self.stdout.write('  ✓ Product filter_options')

        # 8. Reviews
        Review.objects.all().delete()
        for r_data in data.get('Review', []):
            u_id = user_map.get(r_data.get('user'))
            if not u_id:
                continue
            Review.objects.create(
                product_id=product_map.get(r_data['product']),
                user_id=u_id,
                rating=r_data['rating'],
                text=r_data.get('text', ''),
                is_approved=r_data.get('is_approved', False),
            )
        self.stdout.write(f'  ✓ Reviews')

        # 9. Users
        User.objects.all().delete()
        user_map = {}  # pk -> new_pk
        for u_data in data.get('User', []):
            u = User.objects.create(
                email=u_data['email'],
                username=u_data.get('username', u_data['email']),
                first_name=u_data.get('first_name', ''),
                last_name=u_data.get('last_name', ''),
                role=u_data.get('role', 'customer'),
                phone=u_data.get('phone', ''),
                email_confirmed=u_data.get('email_confirmed', False),
                is_staff=u_data.get('role') in ('manager', 'admin'),
                is_superuser=u_data.get('role') == 'admin',
            )
            if u.is_superuser or u.is_staff:
                u.set_password('Admin123!')
            else:
                u.set_password('User123!')
            u.save()
            user_map[u_data['pk']] = u.pk
        self.stdout.write(f'  ✓ Users ({len(user_map)})')

        # 10. Addresses
        Address.objects.all().delete()
        for a_data in data.get('Address', []):
            u_id = user_map.get(a_data.get('user'))
            if not u_id:
                continue
            Address.objects.create(
                user_id=u_id,
                label=a_data.get('label', ''),
                city=a_data.get('city', ''),
                street=a_data.get('street', ''),
                apartment=a_data.get('apartment', ''),
                postal_code=a_data.get('postal_code', ''),
                is_default=a_data.get('is_default', False),
            )
        self.stdout.write(f'  ✓ Addresses')

        # 11. Orders
        Order.objects.all().delete()
        order_map = {}  # old_pk -> new_pk
        for o_data in data.get('Order', []):
            o = Order.objects.create(
                user_id=user_map.get(o_data.get('user')) if o_data.get('user') else None,
                session_key=o_data.get('session_key', ''),
                guest_email=o_data.get('guest_email', ''),
                guest_name=o_data.get('guest_name', ''),
                guest_phone=o_data.get('guest_phone', ''),
                status=o_data.get('status', 'pending'),
                payment_method=o_data.get('payment_method', 'cash'),
                payment_status=o_data.get('payment_status', 'pending'),
                delivery_city=o_data.get('delivery_city', ''),
                delivery_street=o_data.get('delivery_street', ''),
                delivery_apartment=o_data.get('delivery_apartment', ''),
                delivery_postal_code=o_data.get('delivery_postal_code', ''),
                comment=o_data.get('comment', ''),
                promo_code=o_data.get('promo_code', ''),
                subtotal=o_data.get('subtotal', 0),
                delivery_cost=o_data.get('delivery_cost', 0),
                total=o_data.get('total', 0),
            )
            order_map[o_data['pk']] = o.pk
        self.stdout.write(f'  ✓ Orders ({len(order_map)})')

        # 12. OrderItems
        OrderItem.objects.all().delete()
        for i_data in data.get('OrderItem', []):
            OrderItem.objects.create(
                order_id=order_map.get(i_data.get('order')),
                product_id=product_map.get(i_data['product']),
                product_name=i_data.get('product_name', ''),
                product_article=i_data.get('product_article', ''),
                variant_id=variant_map.get(i_data.get('variant_id')) if i_data.get('variant_id') else None,
                price=i_data.get('price', 0),
                quantity=i_data.get('quantity', 1),
            )

        # 13. StatusHistory
        StatusHistory.objects.all().delete()
        for h_data in data.get('StatusHistory', []):
            created_by_id = user_map.get(h_data.get('created_by'))
            StatusHistory.objects.create(
                order_id=order_map.get(h_data.get('order')),
                status=h_data.get('status', 'pending'),
                comment=h_data.get('comment', ''),
                created_by_id=created_by_id,
            )
        self.stdout.write('  ✓ OrderItems + StatusHistory')

        # 14. Carts
        Cart.objects.all().delete()
        cart_map = {}  # old_cart_pk -> new_cart_pk
        cart_user_map = {}  # old_user_pk -> new_cart_pk (for cartitems)
        for c_data in data.get('Cart', []):
            c = Cart.objects.create(
                user_id=user_map.get(c_data.get('user')) if c_data.get('user') else None,
                session_key=c_data.get('session_key', ''),
            )
            cart_map[c_data['pk']] = c.pk
            if c_data.get('user'):
                cart_user_map[c_data['user']] = c.pk
        self.stdout.write(f'  ✓ Carts')

        # 15. CartItems
        CartItem.objects.all().delete()
        for ci_data in data.get('CartItem', []):
            cart_pk = ci_data.get('cart')
            if not cart_pk or cart_pk not in cart_map:
                continue
            CartItem.objects.create(
                cart_id=cart_map[cart_pk],
                product_id=product_map.get(ci_data['product']),
                variant_id=variant_map.get(ci_data.get('variant_id')) if ci_data.get('variant_id') else None,
                quantity=ci_data.get('quantity', 1),
            )
        self.stdout.write('  ✓ CartItems')

        # 16. Pages
        Page.objects.all().delete()
        page_map = {}
        for p_data in data.get('Page', []):
            p = Page.objects.create(
                slug=p_data['slug'],
                title=p_data['title'],
                meta_description=p_data.get('meta_description', ''),
                is_active=p_data.get('is_active', True),
            )
            page_map[p_data['slug']] = p.pk

        PageSection.objects.all().delete()
        for s_data in data.get('PageSection', []):
            image_path = s_data.get('image', '')
            PageSection.objects.create(
                page_id=page_map.get(s_data.get('page')),
                key=s_data.get('key', ''),
                label=s_data.get('label', ''),
                text=s_data.get('text', ''),
                image=image_path,
                link=s_data.get('link', ''),
                is_visible=s_data.get('is_visible', True),
                sort_order=s_data.get('sort_order', 0),
            )
        self.stdout.write(f'  ✓ Pages ({len(page_map)})')

        # 17. Banners
        Banner.objects.all().delete()
        for b_data in data.get('Banner', []):
            image_path = b_data.get('image', '')
            Banner.objects.create(
                title=b_data['title'],
                subtitle=b_data.get('subtitle', ''),
                button_text=b_data.get('button_text', ''),
                button_link=b_data.get('button_link', ''),
                image=image_path,
                sort_order=b_data.get('sort_order', 0),
                is_active=b_data.get('is_active', True),
            )
        self.stdout.write('  ✓ Banners')

        # 18. Subscribers
        Subscriber.objects.all().delete()
        for s_data in data.get('Subscriber', []):
            unsubscribed = s_data.get('unsubscribed_at')
            Subscriber.objects.create(
                email=s_data['email'],
                name=s_data.get('name', ''),
                is_active=s_data.get('is_active', True),
                confirm_token=s_data.get('confirm_token', ''),
                is_confirmed=s_data.get('is_confirmed', False),
                subscribed_at=s_data.get('subscribed_at') or None,
                unsubscribed_at=unsubscribed if unsubscribed else None,
            )
        self.stdout.write(f'  ✓ Subscribers')

        # 19. Favorites
        Favorite.objects.all().delete()
        for f_data in data.get('Favorite', []):
            u_id = user_map.get(f_data.get('user_id'))
            if not u_id:
                continue
            Favorite.objects.create(user_id=u_id, product_id=product_map.get(f_data.get('product_id')))
        self.stdout.write('  ✓ Favorites')

        # Reset SQLite auto-increment for SQLite
        if connection.vendor == 'sqlite':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence")

        self.stdout.write(self.style.SUCCESS('\n✅  Import complete!\n'))
        self.stdout.write('  Passwords: admins/managers = Admin123!, users = User123!')
        self.stdout.write('  Run `python manage.py collectstatic` if needed.\n')

    def _flush(self):
        from apps.orders.models import Order, OrderItem, StatusHistory
        from apps.cart.models import Cart, CartItem
        for M in [StatusHistory, OrderItem, Order, CartItem, Cart, Favorite,
                  ProductVariant, ProductImage, Product,
                  SubSubCategory, SubCategory, Category,
                  FilterOption, FilterGroup, Brand,
                  PageSection, Page, Banner, Subscriber]:
            M.objects.all().delete()
        User.objects.all().delete()
        if connection.vendor == 'sqlite':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence")