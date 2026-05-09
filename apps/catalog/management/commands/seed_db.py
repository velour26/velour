"""
python manage.py seed_db

Заполняет БД:
  - Настройки сайта VELOUR
  - Категории / подкатегории / подподкатегории
  - Группы фильтров и опции (цвет, размер, материал, сезон, стиль, бренд)
  - Бренды
  - 110+ товаров с вариантами и 3+ изображениями каждый
  - 2 admin, 3 manager, 20 customer — у каждого история заказов и корзина
  - CMS-страницы (главная, о нас, доставка, контакты, возврат, оферта, политика)
"""

import os, random, shutil, hashlib, urllib.request
from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.files import File
from django.conf import settings

from faker import Faker

fake = Faker('ru_RU')
User = get_user_model()

# Нормальные русские имена для пользователей
MALE_NAMES = [
    ('Александр', 'Иванов'), ('Дмитрий', 'Смирнов'), ('Максим', 'Кузнецов'),
    ('Андрей', 'Попов'), ('Алексей', 'Васильев'), ('Артём', 'Петров'),
    ('Илья', 'Соколов'), ('Кирилл', 'Михайлов'), ('Михаил', 'Новиков'),
    ('Роман', 'Фёдоров'), ('Никита', 'Морозов'), ('Павел', 'Волков'),
]
FEMALE_NAMES = [
    ('Анна', 'Иванова'), ('Мария', 'Смирнова'), ('Елена', 'Кузнецова'),
    ('Ольга', 'Попова'), ('Наталья', 'Васильева'), ('Татьяна', 'Петрова'),
    ('Юлия', 'Соколова'), ('Екатерина', 'Михайлова'), ('Дарья', 'Новикова'),
    ('Светлана', 'Фёдорова'), ('Полина', 'Морозова'), ('Виктория', 'Волкова'),
    ('Алина', 'Козлова'), ('Ксения', 'Лебедева'), ('Валерия', 'Семёнова'),
    ('Диана', 'Егорова'), ('Вероника', 'Павлова'), ('Кристина', 'Козлова'),
    ('Ирина', 'Степанова'), ('Надежда', 'Орлова'),
]
ALL_NAMES = MALE_NAMES + FEMALE_NAMES

# ─── colour palette ──────────────────────────────────────────────────────────
COLORS = [
    ('Чёрный', '#000000'), ('Белый', '#FFFFFF'), ('Серый', '#808080'),
    ('Бежевый', '#C8A882'), ('Молочный', '#F5F0E8'), ('Кремовый', '#FFFDD0'),
    ('Коричневый', '#795548'), ('Красный', '#E53935'), ('Бордовый', '#7B1FA2'),
    ('Розовый', '#F06292'), ('Персиковый', '#FFAB91'), ('Синий', '#1E88E5'),
    ('Голубой', '#81D4FA'), ('Темно-синий', '#0D47A1'), ('Зелёный', '#43A047'),
    ('Хаки', '#8D6E63'), ('Оливковый', '#827717'), ('Жёлтый', '#FDD835'),
    ('Оранжевый', '#FB8C00'), ('Лавандовый', '#CE93D8'),
]

SIZES_CLOTHES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
SIZES_SHOES   = ['36', '37', '38', '39', '40', '41', '42', '43']

MATERIALS = ['Хлопок', 'Лён', 'Вискоза', 'Полиэстер', 'Шерсть', 'Кашемир',
             'Шёлк', 'Акрил', 'Нейлон', 'Деним', 'Велюр', 'Замша']

SEASONS = ['Весна/Лето', 'Осень/Зима', 'Всесезонный']

STYLES = ['Casual', 'Деловой', 'Спортивный', 'Романтический',
          'Уличный', 'Классический', 'Минимализм', 'Бохо']

BRANDS = [
    # Российские
    'Befree', 'Love Republic', 'LIME', '12 STOREEZ', 'ZARINA',
    'Concept Club', 'ТВОЕ', 'Incity',
    # Международные
    'Zara', 'H&M', 'Mango', 'Reserved', 'COS', 'Massimo Dutti',
]

# ─── catalog structure ───────────────────────────────────────────────────────
CATALOG = {
    'Женщинам': {
        'Верхняя одежда': {
            'subs': ['Пальто', 'Куртки', 'Плащи', 'Шубы'],
            'sizes': SIZES_CLOTHES,
        },
        'Платья и юбки': {
            'subs': ['Платья', 'Юбки', 'Комбинезоны'],
            'sizes': SIZES_CLOTHES,
        },
        'Блузки и рубашки': {
            'subs': ['Блузки', 'Рубашки', 'Топы'],
            'sizes': SIZES_CLOTHES,
        },
        'Брюки и джинсы': {
            'subs': ['Брюки', 'Джинсы', 'Леггинсы'],
            'sizes': SIZES_CLOTHES,
        },
        'Трикотаж': {
            'subs': ['Свитеры', 'Кардиганы', 'Водолазки'],
            'sizes': SIZES_CLOTHES,
        },
    },
    'Мужчинам': {
        'Верхняя одежда': {
            'subs': ['Куртки', 'Пальто', 'Бомберы'],
            'sizes': SIZES_CLOTHES,
        },
        'Рубашки и поло': {
            'subs': ['Рубашки', 'Поло', 'Футболки'],
            'sizes': SIZES_CLOTHES,
        },
        'Брюки и джинсы': {
            'subs': ['Брюки', 'Джинсы', 'Шорты'],
            'sizes': SIZES_CLOTHES,
        },
        'Спортивная одежда': {
            'subs': ['Худи', 'Свитшоты', 'Спортивные костюмы'],
            'sizes': SIZES_CLOTHES,
        },
    },
    'Аксессуары': {
        'Сумки': {
            'subs': ['Сумки через плечо', 'Рюкзаки', 'Клатчи'],
            'sizes': [],
        },
        'Ремни и пояса': {
            'subs': ['Ремни', 'Пояса'],
            'sizes': [],
        },
        'Шарфы и платки': {
            'subs': ['Шарфы', 'Платки', 'Шали'],
            'sizes': [],
        },
    },
}

# ─── product name templates ───────────────────────────────────────────────────
PRODUCT_NAMES = {
    'Пальто':      ['Пальто из шерсти', 'Классическое пальто', 'Пальто оверсайз', 'Двубортное пальто', 'Пальто кокон'],
    'Куртки':      ['Куртка утеплённая', 'Стёганая куртка', 'Ветровка', 'Куртка-бомбер', 'Парка'],
    'Плащи':       ['Тренч классический', 'Тренч с поясом', 'Плащ-макинтош'],
    'Шубы':        ['Шуба из эко-меха', 'Полушубок', 'Жилет из меха'],
    'Платья':      ['Платье-рубашка', 'Платье миди', 'Платье макси', 'Коктейльное платье', 'Платье с запахом', 'Сарафан'],
    'Юбки':        ['Юбка-карандаш', 'Плиссированная юбка', 'Юбка миди', 'Юбка макси', 'Мини-юбка'],
    'Комбинезоны': ['Комбинезон брючный', 'Комбинезон с шортами', 'Комбинезон с юбкой'],
    'Блузки':      ['Блузка с рюшами', 'Шёлковая блузка', 'Блузка с бантом', 'Офисная блузка'],
    'Рубашки':     ['Рубашка оверсайз', 'Рубашка-бойфренд', 'Рубашка в клетку', 'Джинсовая рубашка', 'Льняная рубашка'],
    'Топы':        ['Топ с бретелями', 'Корсетный топ', 'Топ с открытой спиной'],
    'Брюки':       ['Брюки прямые', 'Брюки-кюлоты', 'Брюки-палаццо', 'Брюки зауженные', 'Льняные брюки'],
    'Джинсы':      ['Джинсы скинни', 'Джинсы мом', 'Прямые джинсы', 'Джинсы бойфренд', 'Джинсы широкие'],
    'Леггинсы':    ['Леггинсы базовые', 'Леггинсы со стрелками', 'Кожаные леггинсы'],
    'Свитеры':     ['Свитер оверсайз', 'Тонкий свитер', 'Свитер с горловиной'],
    'Кардиганы':   ['Кардиган длинный', 'Кардиган на пуговицах', 'Кардиган оверсайз'],
    'Водолазки':   ['Водолазка базовая', 'Водолазка укороченная', 'Водолазка с воротником'],
    'Бомберы':     ['Бомбер классический', 'Бомбер с вышивкой', 'Атласный бомбер'],
    'Поло':        ['Поло базовое', 'Поло в полоску', 'Поло с вышивкой'],
    'Футболки':    ['Футболка базовая', 'Футболка оверсайз', 'Лонгслив'],
    'Шорты':       ['Шорты карго', 'Шорты льняные', 'Шорты джинсовые'],
    # Отдельные шаблоны для мужских версий пересекающихся категорий
    'Куртки (муж)':  ['Куртка-анорак', 'Куртка-бомбер мужская', 'Парка мужская', 'Демисезонная куртка', 'Куртка милитари'],
    'Пальто (муж)':  ['Пальто однобортное', 'Пальто с поясом', 'Пальто oversize мужское', 'Двубортное пальто мужское'],
    'Рубашки (муж)': ['Рубашка оксфорд', 'Рубашка в клетку', 'Рубашка-поло длинная', 'Рубашка джинсовая мужская', 'Льняная рубашка мужская'],
    'Брюки (муж)':   ['Брюки чинос', 'Брюки карго', 'Классические брюки', 'Брюки slim fit', 'Льняные брюки мужские'],
    'Джинсы (муж)':  ['Джинсы slim fit', 'Джинсы relaxed fit', 'Джинсы прямого кроя', 'Джинсы loose fit', 'Джинсы tapered'],
    'Худи':        ['Худи оверсайз', 'Худи на молнии', 'Худи с принтом'],
    'Свитшоты':    ['Свитшот базовый', 'Свитшот с принтом', 'Свитшот оверсайз'],
    'Спортивные костюмы': ['Костюм спортивный', 'Костюм велюровый', 'Тренировочный костюм'],
    'Сумки через плечо': ['Сумка кросс-боди', 'Сумка хобо', 'Сумка-мессенджер'],
    'Рюкзаки':     ['Городской рюкзак', 'Кожаный рюкзак', 'Рюкзак мини'],
    'Клатчи':      ['Клатч вечерний', 'Клатч конверт', 'Мини-сумка'],
    'Ремни':       ['Ремень кожаный', 'Ремень плетёный', 'Ремень с пряжкой', 'Ремень тканевый'],
    'Пояса':       ['Пояс корсетный', 'Широкий пояс', 'Пояс-резинка', 'Пояс на цепочке'],
    'Шарфы':       ['Шарф шерстяной', 'Шарф-снуд', 'Шарф палантин'],
    'Платки':      ['Платок шёлковый', 'Платок в горошек', 'Платок с принтом'],
    'Шали':        ['Шаль кашемировая', 'Шаль с бахромой', 'Шаль с узором'],
}

# placeholder image — single neutral grey 1×1 pixel placeholder
PLACEHOLDER_B64 = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
    b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
    b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
    b'\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
)


def make_slug(text, model_class, extra=''):
    base = slugify(text + extra, allow_unicode=True)[:80]
    slug = base
    n = 1
    while model_class.objects.filter(slug=slug).exists():
        slug = f'{base}-{n}'; n += 1
    return slug


def save_placeholder_image(upload_to, filename):
    """Return a django.core.files.File-like object with a placeholder PNG."""
    import io
    buf = io.BytesIO(PLACEHOLDER_B64)
    buf.name = filename
    return File(buf, name=filename)


class Command(BaseCommand):
    help = 'Seed database with VELOUR demo data'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('  flushing existing data...')
            self._flush()

        self.stdout.write(self.style.MIGRATE_HEADING('\n🌱  Seeding VELOUR database\n'))

        site    = self._create_site_settings()
        filters = self._create_filters()
        brands  = self._create_brands()
        cats    = self._create_categories(filters)
        products= self._create_products(cats, filters, brands)
        users   = self._create_users()
        self._create_orders_and_carts(users, products)
        self._create_cms_pages()

        self.stdout.write(self.style.SUCCESS(
            f'\n✅  Done! {len(products)} products, {len(users)} users created.\n'
        ))

    # ─── flush ────────────────────────────────────────────────────────────────
    def _flush(self):
        from django.db import connection
        from apps.orders.models import Order, OrderItem, StatusHistory
        from apps.cart.models import Cart, CartItem
        from apps.catalog.models import (Product, ProductImage, ProductVariant,
                                         Category, SubCategory, SubSubCategory,
                                         FilterGroup, FilterOption, Brand, Review)
        from apps.pages.models import SiteSettings, Page, PageSection, Banner
        from apps.newsletter.models import Subscriber
        for M in [StatusHistory, OrderItem, Order, CartItem, Cart, Review,
                  ProductVariant, ProductImage, Product,
                  SubSubCategory, SubCategory, Category,
                  FilterOption, FilterGroup, Brand,
                  PageSection, Page, Banner, Subscriber]:
            M.objects.all().delete()
        User.objects.all().delete()
        # Reset SQLite auto-increment counters so IDs start from 1
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence")

    # ─── site settings ────────────────────────────────────────────────────────
    def _create_site_settings(self):
        from apps.pages.models import SiteSettings
        s, _ = SiteSettings.objects.get_or_create(pk=1)
        s.site_name = 'VELOUR'
        s.site_description = 'Магазин современной одежды. Качество, стиль и комфорт в каждой вещи.'
        s.phone = '+7 (800) 555-35-35'
        s.email = 'hello@velour.ru'
        s.address = 'Курск, ул. Ленина, д. 30'
        s.vk_url = 'https://vk.com/velour'
        s.telegram_url = 'https://t.me/velour'
        s.delivery_info = (
            'Доставка курьером по Москве: 1–2 рабочих дня, 300 ₽.\n'
            'Доставка по России (СДЭК, Почта России): 3–7 рабочих дней, от 300 ₽.\n'
            'Бесплатная доставка при заказе от 5 000 ₽.\n'
            'Самовывоз из пункта выдачи — бесплатно.'
        )
        s.return_policy = (
            'Возврат товара в течение 14 дней с момента получения.\n'
            'Товар должен быть в оригинальной упаковке, с ярлыками, без следов носки.'
        )
        s.free_delivery_from = Decimal('5000.00')
        s.save()
        self.stdout.write('  ✓ SiteSettings')
        return s

    # ─── filters ──────────────────────────────────────────────────────────────
    def _create_filters(self):
        from apps.catalog.models import FilterGroup, FilterOption
        groups = {}

        def make_group(name, slug, filter_type, options):
            g, _ = FilterGroup.objects.get_or_create(slug=slug, defaults={
                'name': name, 'filter_type': filter_type
            })
            opts = {}
            for i, opt in enumerate(options):
                val, color = (opt if isinstance(opt, tuple) else (opt, ''))
                o_slug = slugify(val, allow_unicode=True)[:50] or f'opt-{i}'
                o, _ = FilterOption.objects.get_or_create(
                    group=g, slug=o_slug,
                    defaults={'value': val, 'color_code': color, 'sort_order': i}
                )
                opts[val] = o
            groups[slug] = (g, opts)
            return g, opts

        make_group('Цвет', 'color', 'color', COLORS)
        make_group('Размер', 'size', 'checkbox', SIZES_CLOTHES)
        make_group('Материал', 'material', 'checkbox', MATERIALS)
        make_group('Сезон', 'season', 'checkbox', SEASONS)
        make_group('Стиль', 'style', 'checkbox', STYLES)

        self.stdout.write(f'  ✓ FilterGroups ({len(groups)})')
        return groups

    # ─── brands ───────────────────────────────────────────────────────────────
    def _create_brands(self):
        from apps.catalog.models import Brand
        brand_objs = {}
        for name in BRANDS:
            slug = slugify(name, allow_unicode=True)[:50]
            b, _ = Brand.objects.get_or_create(slug=slug, defaults={'name': name})
            brand_objs[name] = b
        self.stdout.write(f'  ✓ Brands ({len(brand_objs)})')
        return brand_objs

    # ─── categories ───────────────────────────────────────────────────────────
    def _create_categories(self, filters):
        from apps.catalog.models import Category, SubCategory, SubSubCategory
        cat_data = {}
        category_images = {
            0: 'categories/female.jpg',
            1: 'categories/male.jpg',
            2: 'categories/acs.jpg',
        }

        for ci, (cat_name, subcats) in enumerate(CATALOG.items()):
            slug = make_slug(cat_name, Category)
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={
                'name': cat_name, 'sort_order': ci, 'is_active': True
            })
            if not cat.image and ci in category_images:
                cat.image = category_images[ci]
                cat.save(update_fields=['image'])
            # attach all filter groups to category
            for g_slug, (g, _) in filters.items():
                cat.filter_groups.add(g)

            cat_data[cat_name] = {'obj': cat, 'subs': {}}

            for si, (sub_name, sub_info) in enumerate(subcats.items()):
                sub_slug = make_slug(sub_name, SubCategory)
                sub, _ = SubCategory.objects.get_or_create(slug=sub_slug, defaults={
                    'category': cat, 'name': sub_name, 'sort_order': si
                })
                cat_data[cat_name]['subs'][sub_name] = {'obj': sub, 'subsubs': {}, 'sizes': sub_info['sizes']}

                for ssi, subsub_name in enumerate(sub_info.get('subs', [])):
                    ss_slug = make_slug(subsub_name, SubSubCategory)
                    ss, _ = SubSubCategory.objects.get_or_create(slug=ss_slug, defaults={
                        'subcategory': sub, 'name': subsub_name, 'sort_order': ssi
                    })
                    cat_data[cat_name]['subs'][sub_name]['subsubs'][subsub_name] = ss

        self.stdout.write(f'  ✓ Categories')
        return cat_data

    # ─── products ─────────────────────────────────────────────────────────────
    def _create_products(self, cats, filters, brands):
        from apps.catalog.models import Product, ProductImage, ProductVariant, FilterOption
        color_group, color_opts = filters['color']
        _, mat_opts = filters['material']
        _, season_opts = filters['season']
        _, style_opts = filters['style']

        products = []
        article_counter = 1000

        for cat_name, cat_info in cats.items():
            for sub_name, sub_info in cat_info['subs'].items():
                for subsub_name, subsub_obj in sub_info['subsubs'].items():
                    # Для мужских категорий используем отдельные шаблоны
                    # чтобы избежать дублей с женскими товарами
                    is_male = (cat_name == 'Мужчинам')
                    male_key = f'{subsub_name} (муж)'
                    if is_male and male_key in PRODUCT_NAMES:
                        name_templates = PRODUCT_NAMES[male_key]
                    else:
                        name_templates = PRODUCT_NAMES.get(subsub_name, [f'{subsub_name} базовый'])
                    count = max(3, 9 // max(1, len(sub_info['subsubs'])))

                    # Shuffle templates so each product gets a unique name
                    shuffled = name_templates[:]
                    random.shuffle(shuffled)
                    for i in range(count):
                        full_name = shuffled[i % len(shuffled)]

                        price = Decimal(str(random.choice([
                            990, 1290, 1490, 1790, 1990, 2490, 2990, 3490,
                            3990, 4490, 4990, 5990, 6990, 7990, 8990, 9990,
                            12990, 14990, 19990
                        ])))
                        has_discount = random.random() < 0.35
                        old_price = price * Decimal('1.' + str(random.randint(15, 50))) if has_discount else None

                        article_counter += random.randint(1, 9)
                        article = f'VL-{article_counter:05d}'

                        slug = make_slug(full_name, Product, f'-{article_counter}')

                        product = Product.objects.create(
                            category=cat_info['obj'],
                            subcategory=sub_info['obj'],
                            subsubcategory=subsub_obj,
                            brand=random.choice(list(brands.values())),
                            name=full_name,
                            slug=slug,
                            article=article,
                            description=self._gen_description(full_name, subsub_name),
                            composition=self._gen_composition(),
                            price=price,
                            old_price=old_price if has_discount else None,
                            is_active=True,
                            is_featured=random.random() < 0.2,
                            is_new=random.random() < 0.25,
                        )

                        # Filter options
                        mat = random.choice(list(mat_opts.values()))
                        season = random.choice(list(season_opts.values()))
                        style = random.choice(list(style_opts.values()))
                        product.filter_options.set([mat, season, style])

                        # Images (3 placeholder PNGs per product)
                        for img_i in range(3):
                            img_file = save_placeholder_image('products/', f'{article}_{img_i+1}.png')
                            ProductImage.objects.create(
                                product=product,
                                image=img_file,
                                alt=full_name,
                                is_main=(img_i == 0),
                                sort_order=img_i,
                            )

                        # Variants
                        sizes = sub_info['sizes'] or ['One Size']
                        picked_colors = random.sample(list(color_opts.values()), min(3, len(color_opts)))
                        for size in random.sample(sizes, min(4, len(sizes))):
                            for color in picked_colors[:2]:
                                ProductVariant.objects.create(
                                    product=product,
                                    size=size,
                                    color=color,
                                    stock=random.randint(0, 30),
                                    sku=f'{article}-{size}-{color.slug[:4].upper()}',
                                )

                        products.append(product)

        self.stdout.write(f'  ✓ Products ({len(products)})')
        return products

    def _gen_description(self, name, category):
        adj = random.choice(['стильный', 'элегантный', 'современный', 'классический', 'трендовый', 'универсальный'])
        material = random.choice(MATERIALS).lower()
        occasion = random.choice(['офиса', 'прогулки', 'вечернего выхода', 'повседневного образа', 'особых случаев'])
        return (
            f'{name} — {adj} выбор для вашего гардероба. '
            f'Изготовлен из качественного {material}, '
            f'идеально подходит для {occasion}. '
            f'Свободный крой обеспечивает комфорт в течение всего дня. '
            f'Сочетается с различными элементами гардероба, создавая законченный образ.'
        )

    def _gen_composition(self):
        mat1 = random.choice(MATERIALS)
        pct1 = random.randint(50, 95)
        mat2 = random.choice([m for m in MATERIALS if m != mat1])
        pct2 = 100 - pct1
        return f'{mat1} {pct1}%, {mat2} {pct2}%'

    # ─── users ────────────────────────────────────────────────────────────────
    def _create_users(self):
        users = []

        ADMIN_NAMES = [
            ('Сергей',  'Громов'),
            ('Наталья', 'Белова'),
        ]
        MANAGER_NAMES = [
            ('Екатерина', 'Орлова'),
            ('Андрей',    'Титов'),
            ('Юлия',      'Макарова'),
        ]
        PHONES = [
            '+7 (916) 123-45-67', '+7 (926) 234-56-78', '+7 (903) 345-67-89',
            '+7 (985) 456-78-90', '+7 (977) 567-89-01',
        ]

        # 2 admins
        for i in range(1, 3):
            first, last = ADMIN_NAMES[i - 1]
            u, created = User.objects.get_or_create(
                email=f'admin{i}@velour.ru',
                defaults=dict(
                    username=f'admin{i}',
                    first_name=first,
                    last_name=last,
                    role='admin',
                    is_staff=True,
                    is_superuser=True,
                    phone=PHONES[i - 1],
                    email_confirmed=True,
                )
            )
            if created:
                u.set_password('Admin123!')
                u.save()
            users.append(u)

        # 3 managers
        for i in range(1, 4):
            first, last = MANAGER_NAMES[i - 1]
            u, created = User.objects.get_or_create(
                email=f'manager{i}@velour.ru',
                defaults=dict(
                    username=f'manager{i}',
                    first_name=first,
                    last_name=last,
                    role='manager',
                    is_staff=True,
                    is_superuser=True,
                    phone=PHONES[i + 1],
                    email_confirmed=True,
                )
            )
            if created:
                u.set_password('Manager123!')
                u.save()
            else:
                if not u.is_superuser:
                    u.is_superuser = True
                    u.save(update_fields=['is_superuser'])
            users.append(u)

        # 20 customers
        shuffled_names = ALL_NAMES[:]
        random.shuffle(shuffled_names)
        customer_phones = [
            '+7 (916) 111-22-33', '+7 (926) 222-33-44', '+7 (903) 333-44-55',
            '+7 (985) 444-55-66', '+7 (977) 555-66-77', '+7 (916) 666-77-88',
            '+7 (926) 777-88-99', '+7 (903) 888-99-00', '+7 (985) 999-00-11',
            '+7 (977) 100-11-22', '+7 (916) 200-22-33', '+7 (926) 300-33-44',
            '+7 (903) 400-44-55', '+7 (985) 500-55-66', '+7 (977) 600-66-77',
            '+7 (916) 700-77-88', '+7 (926) 800-88-99', '+7 (903) 900-99-00',
            '+7 (985) 010-10-10', '+7 (977) 020-20-20',
        ]
        for i in range(20):
            email = f'user{i+1}@example.com'
            first, last = shuffled_names[i % len(shuffled_names)]
            u, created = User.objects.get_or_create(
                email=email,
                defaults=dict(
                    username=f'user{i+1}',
                    first_name=first,
                    last_name=last,
                    role='customer',
                    phone=customer_phones[i],
                    email_confirmed=True,
                )
            )
            if created:
                u.set_password('User123!')
                u.save()

            # Address
            from apps.accounts.models import Address
            if not u.addresses.exists():
                Address.objects.create(
                    user=u,
                    label='Домой',
                    city=fake.city(),
                    street=fake.street_address(),
                    apartment=str(random.randint(1, 200)),
                    postal_code=fake.postcode(),
                    is_default=True,
                )
            users.append(u)

        self.stdout.write(f'  ✓ Users ({len(users)})')
        return users

    # ─── orders & carts ───────────────────────────────────────────────────────
    def _create_orders_and_carts(self, users, products):
        from apps.orders.models import Order, OrderItem, StatusHistory
        from apps.cart.models import Cart, CartItem

        customers = [u for u in users if u.role == 'customer']
        statuses = list(Order.Status)
        payment_methods = list(Order.PaymentMethod)

        for user in customers:
            # 1–4 past orders per user
            n_orders = random.randint(1, 4)
            for _ in range(n_orders):
                items_for_order = random.sample(products, random.randint(1, 4))
                subtotal = sum(p.price for p in items_for_order)
                delivery = Decimal('0') if subtotal >= 5000 else Decimal('300')
                total = subtotal + delivery

                addr = user.addresses.first()
                days_ago = random.randint(1, 180)
                created_at = timezone.now() - timedelta(days=days_ago)

                status = random.choice(statuses)
                order = Order.objects.create(
                    user=user,
                    status=status,
                    payment_method=random.choice(payment_methods),
                    payment_status='paid' if status not in ('pending', 'cancelled') else 'pending',
                    delivery_city=addr.city if addr else fake.city(),
                    delivery_street=addr.street if addr else fake.street_address(),
                    delivery_apartment=addr.apartment if addr else '',
                    delivery_postal_code=addr.postal_code if addr else fake.postcode(),
                    subtotal=subtotal,
                    delivery_cost=delivery,
                    total=total,
                )
                # Override created_at
                Order.objects.filter(pk=order.pk).update(created_at=created_at)

                for product in items_for_order:
                    qty = random.randint(1, 3)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        product_article=product.article,
                        price=product.price,
                        quantity=qty,
                    )

                StatusHistory.objects.create(order=order, status=Order.Status.PENDING)
                if status not in ('pending',):
                    StatusHistory.objects.create(order=order, status=Order.Status.CONFIRMED)
                if status in ('shipped', 'delivered'):
                    StatusHistory.objects.create(order=order, status=Order.Status.SHIPPED)
                if status == 'delivered':
                    StatusHistory.objects.create(order=order, status=Order.Status.DELIVERED)

            # Active cart with 1–3 items
            cart, _ = Cart.objects.get_or_create(user=user)
            for product in random.sample(products, random.randint(1, 3)):
                CartItem.objects.get_or_create(
                    cart=cart, product=product, variant=None,
                    defaults={'quantity': random.randint(1, 2)}
                )

        self.stdout.write(f'  ✓ Orders & carts')

    # ─── cms pages ────────────────────────────────────────────────────────────
    def _create_cms_pages(self):
        from apps.pages.models import Page, PageSection, Banner

        pages_data = [
            ('home', 'Главная', [
                ('hero_eyebrow', 'Лейбл над заголовком', 'Новая коллекция 2025', ''),
                ('hero_title', 'Заголовок героя', 'Стиль,\nкоторый\nговорит за вас', ''),
                ('cta_title', 'CTA заголовок', 'Скидки до 50% на избранное', ''),
                ('cta_subtitle', 'CTA подзаголовок', 'Успейте купить до конца недели — самые популярные позиции уходят быстро', ''),
                ('cta_button', 'CTA кнопка', 'Смотреть акции', '/catalog/?has_discount=true'),
            ]),
            ('about', 'О нас', [
                ('intro', 'Вступление', 'VELOUR — это магазин современной одежды, созданный для тех, кто ценит качество, стиль и комфорт. Мы отбираем лучшие ткани и работаем с проверенными производителями.', ''),
                ('mission', 'Миссия', 'Наша миссия — делать качественную одежду доступной для каждого. Мы верим, что хороший стиль не должен стоить целое состояние.', ''),
                ('team', 'Команда', 'Наша команда — это профессионалы в области моды, которые следят за трендами и тщательно отбирают каждую вещь в коллекцию.', ''),
            ]),
            ('delivery', 'Доставка и оплата', [
                ('delivery_main', 'Способы доставки', 'Курьером по Москве: 1–2 дня, 300 ₽. Бесплатно при заказе от 5 000 ₽.\nПо России (СДЭК/Почта): 3–7 дней, от 300 ₽.\nСамовывоз из ПВЗ — бесплатно.', ''),
                ('payment_main', 'Способы оплаты', 'Онлайн — картой Visa, Mastercard, МИР или через СБП.\nПри получении — наличными или картой курьеру.', ''),
            ]),
            ('contacts', 'Контакты', [
                ('contact_info', 'Контактная информация', 'Телефон: +7 (800) 555-35-35 (бесплатно)\nEmail: hello@velour.ru\nРежим работы: ПН–ПТ 9:00–18:00', ''),
                ('social_info', 'Социальные сети', 'Следите за нами ВКонтакте и Telegram — там первыми узнаете о новинках и акциях.', ''),
            ]),
            ('returns', 'Возврат и обмен', [
                ('return_policy', 'Условия возврата', 'Вы можете вернуть товар в течение 14 дней с момента получения.\nТовар должен быть в оригинальной упаковке с ярлыками, без следов носки.', ''),
                ('return_process', 'Как оформить возврат', '1. Свяжитесь с нами по телефону или email\n2. Мы пришлём инструкцию по возврату\n3. Отправьте товар удобным способом\n4. После проверки вернём деньги в течение 5 рабочих дней.', ''),
            ]),
            ('privacy', 'Политика конфиденциальности', [
                ('intro', 'Введение', 'Настоящая Политика конфиденциальности регулирует порядок сбора, использования и хранения персональных данных пользователей сайта VELOUR.', ''),
                ('data_collected', 'Какие данные мы собираем', 'Имя и фамилия, адрес электронной почты, номер телефона, адрес доставки. Данные собираются исключительно для оформления и доставки заказов.', ''),
                ('data_use', 'Использование данных', 'Ваши данные используются для: обработки заказов и доставки, отправки уведомлений о статусе заказа, улучшения сервиса. Мы не передаём данные третьим лицам, кроме случаев, необходимых для доставки.', ''),
                ('cookies', 'Файлы cookie', 'Сайт использует файлы cookie для корректной работы корзины и улучшения пользовательского опыта. Отключение cookie может ограничить функциональность сайта.', ''),
                ('contacts', 'Контакты по вопросам', 'По вопросам обработки персональных данных обращайтесь: hello@velour.ru', ''),
            ]),
            ('terms', 'Публичная оферта', [
                ('intro', 'Общие положения', 'Настоящий документ является публичной офертой ООО «VELOUR» и определяет условия продажи товаров через интернет-магазин velour.ru.', ''),
                ('order', 'Оформление заказа', 'Заказ считается оформленным после подтверждения по электронной почте. Цены на товары указаны в рублях и включают НДС. VELOUR оставляет за собой право изменять цены без предварительного уведомления.', ''),
                ('payment', 'Оплата', 'Оплата производится картой онлайн, через СБП или наличными при получении. Заказ резервируется после поступления оплаты.', ''),
                ('delivery', 'Доставка', 'Сроки и стоимость доставки указаны в разделе «Доставка и оплата». Риск случайной гибели товара переходит к покупателю с момента передачи заказа службе доставки.', ''),
                ('return', 'Возврат', 'Порядок возврата регулируется Законом РФ «О защите прав потребителей» и описан в разделе «Возврат и обмен».', ''),
            ]),
        ]

        for slug, title, sections in pages_data:
            page, _ = Page.objects.get_or_create(slug=slug, defaults={'title': title, 'is_active': True})
            for order, (key, label, text, link) in enumerate(sections):
                PageSection.objects.get_or_create(
                    page=page, key=key,
                    defaults={'label': label, 'text': text, 'link': link, 'sort_order': order, 'is_visible': True}
                )

        # Default banner
        if not Banner.objects.exists():
            img = save_placeholder_image('banners/', 'hero_banner.png')
            Banner.objects.create(
                title='Новая коллекция VELOUR',
                subtitle='Откройте для себя современную одежду для любого случая',
                button_text='Смотреть коллекцию',
                button_link='/catalog/',
                image=img,
                sort_order=0,
                is_active=True,
            )

        self.stdout.write('  ✓ CMS Pages & Banners')
