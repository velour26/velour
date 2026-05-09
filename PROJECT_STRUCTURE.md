# Project Structure Documentation

Документ описывает архитектуру, ответственность модулей и соглашения по данным/файлам для проекта `VELOUR`.

## 1. Обзор архитектуры

Проект построен как Django-монолит с разделением на прикладные модули внутри каталога `apps/`.

Основные домены:

- `config` - глобальная конфигурация Django: `settings`, `urls`, `middleware`, `wsgi`, `asgi`.
- `apps.pages` - главная страница, CMS-страницы, баннеры, настройки сайта и контекст для публичных шаблонов.
- `apps.catalog` - каталог, категории, подкатегории, бренды, товары, изображения, варианты, фильтры, избранное и отзывы.
- `apps.cart` - корзина и позиции корзины для гостей и пользователей.
- `apps.orders` - оформление, хранение и просмотр заказов, позиции заказа и история статусов.
- `apps.accounts` - кастомный пользователь, роли, адреса и server-rendered страницы аккаунта.
- `apps.newsletter` - подписчики, рассылки, подтверждение подписки и отписка.
- `apps.api` - REST API, сериализаторы, фильтры, endpoints и email helper.

Архитектурно проект сочетает две модели доставки:

- публичный UI рендерится через Django templates;
- интерактивные сценарии получают и изменяют данные через REST API.

## 2. Корневая структура

```text
.
├─ apps/
│  ├─ accounts/
│  ├─ api/
│  ├─ cart/
│  ├─ catalog/
│  ├─ newsletter/
│  ├─ orders/
│  └─ pages/
├─ config/
├─ docs/
├─ media/
├─ scripts/
├─ seed_data/
├─ static/
├─ templates/
├─ .env
├─ .env.example
├─ db.sqlite3
├─ manage.py
├─ requirements.txt
├─ build.sh
├─ Dockerfile
├─ Procfile
├─ render.yaml
├─ README.md
└─ PROJECT_STRUCTURE.md
```

Примечания:

- Django-проект живёт в корне репозитория, рядом с `manage.py`;
- `apps/` содержит прикладные Django-модули;
- `config/` содержит настройки и корневой URLConf;
- `docs/` содержит инструкции по PostgreSQL/Render и переносу данных;
- `seed_data/` и `media/` содержат demo-изображения и runtime media;
- `build.sh`, `Dockerfile`, `Procfile` и `render.yaml` относятся к деплою.

## 3. Django-модули

### 3.1 `config`

Назначение:

- глобальные настройки Django;
- корневой URLConf;
- middleware для админки;
- точки входа WSGI/ASGI.

Ключевые файлы:

- `settings.py` - `INSTALLED_APPS`, SQLite fallback, PostgreSQL через `DATABASE_URL`, static/media, DRF, Jazzmin, email, CORS, logging;
- `urls.py` - объединяет `/admin/`, `/api/`, публичные страницы и app-level маршруты;
- `middleware.py` - project middleware;
- `wsgi.py`, `asgi.py` - production entrypoints.

Высокоуровневый роутинг:

- `/admin/` - Django admin + Jazzmin;
- `/api/` - DRF endpoints из `apps.api`;
- `/` - главная и CMS-страницы из `apps.pages`;
- `/catalog/` - каталог и товарные страницы;
- `/cart/` - корзина;
- `/orders/` - checkout и заказы;
- `/account/` - login/register/profile/password reset;
- `/newsletter/` - подтверждение подписки и отписка.

### 3.2 `apps.pages`

Назначение:

- главная страница;
- статические/CMS-страницы;
- настройки сайта;
- баннеры;
- context processor с глобальными настройками.

Модели:

- `SiteSettings` - singleton-настройки сайта: название, описание, контакты, соцсети, доставка, возврат, порог бесплатной доставки;
- `Page` - CMS-страница с slug, title, meta description и активностью;
- `PageSection` - редактируемая секция страницы;
- `Banner` - баннеры для витринных блоков.

Ключевые файлы:

- `models.py` - настройки сайта, страницы, секции и баннеры;
- `views.py` - `HomeView`, `PageView`;
- `urls.py` - `/`, `/about/`, `/delivery/`, `/contacts/`, `/returns/`, `/privacy/`, `/terms/`;
- `context_processors.py` - site settings в шаблонах;
- `admin.py` - singleton admin для настроек и inline-секции страниц.

### 3.3 `apps.catalog`

Назначение:

- центральный каталог товаров;
- категории, подкатегории и вложенные подкатегории;
- фильтры и опции фильтров;
- бренды;
- товары, изображения и варианты;
- избранное и отзывы;
- management commands для seed/import.

Модели:

- `Category`, `SubCategory`, `SubSubCategory`;
- `FilterGroup`, `FilterOption`;
- `Brand`;
- `Product`, `ProductImage`, `ProductVariant`;
- `Favorite`;
- `Review`.

Ключевые файлы:

- `models.py` - основная модель каталога;
- `views.py` - server-rendered каталог, категория, товар, избранное;
- `urls.py` - `/catalog/`, `/catalog/favorites/`, category/product routes;
- `admin.py` - inline-изображения и варианты, фильтры, превью, остатки;
- `management/commands/seed_db.py` - demo seed;
- `management/commands/import_images.py` - импорт demo-изображений.

Особенности:

- product lookup на публичных страницах использует slug;
- встроенный `<slug:>` не подходит для кириллических slug, поэтому в `urls.py` используется `<str:category_slug>`;
- односложный URL `/catalog/<product_slug>/` поддержан как fallback: если slug не является категорией, но является товаром, `CategoryView` редиректит на канонический `/catalog/<category_slug>/<product_slug>/`;
- `Product.main_image` берёт главное изображение или первое доступное;
- `ProductImage.save()` поддерживает только одно главное изображение на товар.
- новые `Review` создаются с `is_approved=False`; публичные списки, счётчики и рейтинг товара используют только `approved_reviews`.

### 3.4 `apps.cart`

Назначение:

- хранение корзины;
- поддержка гостевой корзины через session key;
- корзина авторизованного пользователя через `OneToOneField`;
- счётчик корзины в шаблонах.

Модели:

- `Cart` - владелец `user` или `session_key`, дата создания/обновления, свойства `total` и `count`;
- `CartItem` - товар, вариант и количество.

Ключевые файлы:

- `models.py`;
- `views.py` - server-rendered `/cart/`;
- `urls.py`;
- `context_processors.py` - `cart_count`;
- `admin.py`.

### 3.5 `apps.orders`

Назначение:

- оформление и хранение заказов;
- позиции заказа;
- история статусов;
- страницы checkout/payment/success/my orders.

Модели:

- `Order` - номер, пользователь/гость, статус, способ оплаты, адрес доставки, суммы, комментарий;
- `OrderItem` - снимок товара, артикула, варианта, цены и количества на момент заказа;
- `StatusHistory` - история изменений статуса.

Ключевые файлы:

- `models.py`;
- `views.py` - checkout, payment, success, мои заказы;
- `urls.py`;
- `admin.py` - inline-позиции, inline-история, badge статуса.

Платёжные методы в модели:

- `cash`;
- `sbp`;
- `card`.

Статусы заказа:

- `pending`, `confirmed`, `paid`, `assembling`, `shipped`, `delivered`, `cancelled`, `returned`.

### 3.6 `apps.accounts`

Назначение:

- кастомный пользователь;
- роли;
- адреса доставки;
- страницы входа, регистрации, профиля и восстановления пароля.

Модели:

- `User` - наследник `AbstractUser`, login по email, role, phone, avatar, email-confirm fields;
- `Address` - адрес пользователя с флагом адреса по умолчанию.

Ключевые файлы:

- `models.py`;
- `views.py`;
- `urls.py`;
- `admin.py` - UserAdmin с inline-адресами;
- `apps.py`.

Роли:

- `customer`;
- `manager`;
- `admin`.

### 3.7 `apps.newsletter`

Назначение:

- подписчики;
- рассылки;
- подтверждение подписки;
- отписка.

Модели:

- `Subscriber` - email, имя, активность, подтверждение, token, даты подписки/отписки;
- `Newsletter` - тема, HTML/text body, статус, дата отправки, количество получателей.

Ключевые файлы:

- `models.py`;
- `views.py`;
- `urls.py`;
- `admin.py` - action отправки рассылки;
- `apps.py`.

### 3.8 `apps.api`

Назначение:

- REST API для frontend-сценариев;
- сериализация доменных моделей;
- фильтрация каталога;
- helper для отправки email.

Структура:

```text
apps/api/
├─ backends/
│  └─ resend.py
├─ filters/
│  └─ catalog.py
├─ serializers/
│  ├─ accounts.py
│  ├─ cart.py
│  ├─ catalog.py
│  └─ orders.py
├─ utils/
│  └─ email.py
├─ views/
│  ├─ accounts.py
│  ├─ cart.py
│  ├─ catalog.py
│  ├─ favorites.py
│  ├─ newsletter.py
│  └─ orders.py
└─ urls.py
```

Основные endpoint-группы:

- catalog: `categories`, `products`, `filters`, `brands`;
- cart: `cart`, `cart/add`, `cart/items/<id>`;
- orders: list/create/detail/cancel;
- accounts: login/logout/register/profile/change-password/addresses;
- favorites: list/status/toggle/sync;
- newsletter: subscribe/confirm/unsubscribe.

## 4. Маршрутизация и потоки

Корневой роутинг описан в `config/urls.py`.

### 4.1 Каталог -> корзина -> заказ

`apps.catalog` хранит товары, варианты, цены и остатки.  
`apps.api.views.catalog` отдаёт товары и фильтры.  
`apps.api.views.cart` создаёт или возвращает корзину по user/session.  
`apps.api.views.orders` создаёт заказ, копирует позиции корзины в `OrderItem`, уменьшает остатки и очищает корзину.  
Шаблоны и JS в `templates/` + `static/js/` дают пользовательский интерфейс.

### 4.2 Профиль и адреса

`apps.accounts` хранит пользователя и адреса.  
`apps.api.views.accounts` отдаёт/обновляет профиль, создаёт адреса и меняет пароль.  
`templates/account/` содержит server-rendered страницы профиля, входа и регистрации.

### 4.3 Избранное

Для пользователя избранное хранится в `catalog.Favorite`.  
Для гостевого режима есть API-синхронизация через cache/session flow в `GuestFavoritesSyncView`.

### 4.4 Отзывы и модерация

`apps.api.views.catalog.ProductViewSet.add_review` создаёт отзыв с `is_approved=False`.  
`ProductDetailView` передаёт в шаблон только `approved_reviews`, `approved_reviews_count` и среднюю оценку по одобренным отзывам.  
До одобрения в админке отзыв не отображается на странице товара, не увеличивает `Отзывы (N)` и не влияет на звёзды рейтинга.

### 4.5 Рассылки

Подписка идёт через `/api/newsletter/subscribe/`.  
Админка хранит подписчиков и черновики рассылок.  
Action `send_newsletter` отправляет письма активным подписчикам через `apps.api.utils.email.send_email`.

## 5. Шаблоны и фронтенд

### 5.1 `templates/`

Основные разделы:

- `templates/base.html` - базовый layout;
- `templates/includes/` - header, footer, product card;
- `templates/pages/` - главная и CMS-страницы;
- `templates/catalog/` - каталог, товар, избранное;
- `templates/cart/` - корзина;
- `templates/orders/` - checkout, оплата, успех, мои заказы, деталка заказа;
- `templates/account/` - login, register, profile, password reset flow;
- `templates/email/` - email layout и письма.

Подход:

- server-rendered страницы отвечают за начальный HTML;
- интерактивность подключается через JS из `static/js`;
- API находится под `/api/`.

### 5.2 `static/`

Основные каталоги:

- `static/css/` - базовые стили, header/footer, каталог, страницы, admin custom;
- `static/js/` - account, cart, catalog, checkout, main;
- `static/images/` - статичные изображения;
- `static/fonts/` - локальные шрифты, если скачаны скриптом.

Ключевые frontend-файлы:

- `static/js/catalog.js`;
- `static/js/cart.js`;
- `static/js/checkout.js`;
- `static/js/account.js`;
- `static/js/main.js`;
- `static/css/admin_custom.css`.

## 6. Медиа и файловые соглашения

### 6.1 `media/`

Содержит загруженные и demo-медиа:

- `media/products/` - изображения товаров;
- `media/categories/` - изображения категорий;
- `media/brands/` - логотипы брендов;
- `media/banners/` - баннеры;
- `media/pages/` - изображения секций страниц;
- `media/avatars/` - аватары пользователей, если загружены.

### 6.2 `seed_data/`

Содержит исходные изображения для demo-каталога и может временно содержать fixture для переноса БД:

```text
seed_data/images/VL-01002/01.jpg
seed_data/images/VL-01002/02.jpg
seed_data/current_db.json
...
```

`import_images.py` сопоставляет артикулы товаров с папками `seed_data/images/<article>/` и переносит изображения в Django media.
`current_db.json` не нужен для обычной разработки; он используется только для разового `loaddata` при переносе SQLite -> PostgreSQL.

### 6.3 Принципы организации

- доменные изображения группируются по назначению;
- demo-изображения отделены от runtime media;
- seed может работать без внешней сети благодаря placeholder-изображениям;
- реальные product images можно восстановить из `seed_data/images/`.

## 7. Seed, роли и служебные команды

Основные management commands:

- `seed_db.py` - наполнение БД demo-данными;
- `import_images.py` - импорт изображений товаров из `seed_data/images/`.
- `dumpdata`/`loaddata` - штатные Django-команды для fixture-переноса данных между SQLite и PostgreSQL.

Скрипты:

- `scripts/download_fonts.py` - загрузка локальных шрифтов;
- `scripts/download_wb_images.py` - загрузка изображений по данным Wildberries/артикулам.

Seed создаёт:

- `admin1@velour.ru`, `admin2@velour.ru` с паролем `Admin123!`;
- `manager1@velour.ru` ... `manager3@velour.ru` с паролем `Manager123!`;
- `user1@example.com` ... `user20@example.com` с паролем `User123!`;
- товары, варианты, остатки, корзины, заказы и CMS-контент.

## 8. Конфигурация и окружения

Основные точки:

- `manage.py`;
- `config/settings.py`;
- `config/urls.py`;
- `.env.example`;
- `requirements.txt`;
- `build.sh`;
- `render.yaml`;
- `docs/POSTGRESQL_RENDER_MIGRATION.md`.

По умолчанию:

- локальная БД - `db.sqlite3`, если `DATABASE_URL` не задан;
- production БД - PostgreSQL через `DATABASE_URL`;
- `MEDIA_ROOT` - `media/`;
- `STATIC_ROOT` - `staticfiles/`;
- `STATICFILES_STORAGE` - WhiteNoise compressed manifest storage;
- язык - `ru-ru`;
- timezone - `Europe/Moscow`;
- кастомный user model - `accounts.User`.

Важные env vars:

- `DATABASE_URL` - подключение PostgreSQL, например Render Internal Database URL;
- `SEED_DEMO_DATA=false` - отключает demo seed в `build.sh`;
- `DJANGO_LOAD_FIXTURE=seed_data/current_db.json` - разово загружает fixture во время build;
- `IMPORT_PRODUCT_IMAGES=true` - пересобирает `ProductImage` из committed `media/products` по префиксу артикула;
- `EMAIL_*` - SMTP-настройки;
- `CORS_ALLOWED_ORIGINS` - внешние frontend origins, если нужны.

`build.sh` выполняет установку зависимостей, `collectstatic`, миграции, загрузку локальных шрифтов, затем опциональный `loaddata` из `DJANGO_LOAD_FIXTURE`, опциональный `import_images --flat-dir media/products --replace` при `IMPORT_PRODUCT_IMAGES=true` и demo seed, если товары отсутствуют и `SEED_DEMO_DATA` не выключен.

## 9. PostgreSQL и перенос данных

Для Render production-сценария:

1. Создать Render Postgres в том же регионе, что и web service.
2. Добавить `DATABASE_URL=<Internal Database URL>` в web service.
3. Если переносится текущая SQLite БД, добавить `SEED_DEMO_DATA=false`.
4. Выгрузить SQLite в `seed_data/current_db.json` через `dumpdata`.
5. На Windows перед `dumpdata` включить UTF-8:

```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
```

6. Закоммитить fixture и задать `DJANGO_LOAD_FIXTURE=seed_data/current_db.json`.
7. Если product image records нужно восстановить из committed `media/products`, задать `IMPORT_PRODUCT_IMAGES=true`.
8. После успешного импорта очистить `DJANGO_LOAD_FIXTURE`; `IMPORT_PRODUCT_IMAGES` можно выключить после проверки картинок.

Подробно: `docs/POSTGRESQL_RENDER_MIGRATION.md`.

## 10. Практика для разработчиков

Рекомендуемый порядок анализа новой задачи:

1. `config/urls.py`
2. нужный app-level `urls.py`
3. нужный `views.py` или `apps/api/views/*.py`
4. если задача про данные - соответствующий `models.py`
5. serializer/filter в `apps/api/`, если меняется API
6. HTML в `templates/`
7. JS/CSS в `static/`

Для каталога:

1. `apps/catalog/models.py`
2. `apps/api/views/catalog.py`
3. `apps/api/serializers/catalog.py`
4. `apps/api/filters/catalog.py`
5. `templates/catalog/`
6. `static/js/catalog.js`
7. `static/css/catalog.css`

Для checkout:

1. `apps/cart/models.py`
2. `apps/orders/models.py`
3. `apps/api/views/cart.py`
4. `apps/api/views/orders.py`
5. `apps/api/serializers/cart.py`
6. `apps/api/serializers/orders.py`
7. `templates/orders/checkout.html`
8. `static/js/checkout.js`

Для админки:

1. `apps/*/admin.py`
2. `config/settings.py` блок `JAZZMIN_SETTINGS`
3. `static/css/admin_custom.css`

## 11. Контроль качества

Минимальная проверка:

```bash
python manage.py check
python manage.py migrate
```

Проверка demo-данных:

```bash
python manage.py seed_db --flush
python manage.py import_images --replace
python manage.py runserver
```

Smoke-проверка страниц:

- `/`
- `/catalog/`
- `/cart/`
- `/orders/checkout/`
- `/account/login/`
- `/account/profile/`
- `/orders/my/`
- `/about/`
- `/delivery/`
- `/admin/`

Smoke-проверка API:

- `/api/categories/`
- `/api/products/`
- `/api/filters/`
- `/api/brands/`
- `/api/cart/`

Для задач, затрагивающих данные:

- проверить миграции;
- проверить seed на чистой БД;
- если меняется production data flow, проверить `dumpdata`/`loaddata` на отдельной базе;
- выборочно открыть admin change forms;
- проверить API serializer output;
- пройти сценарий "товар -> корзина -> checkout -> заказ".
