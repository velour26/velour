# VELOUR - интернет-магазин одежды

VELOUR - полнофункциональный интернет-магазин одежды на Django 5.1 и Django REST Framework. В проекте есть публичный каталог, фильтры, карточки товаров с вариантами, корзина, оформление заказов, личный кабинет, избранное, email-рассылки, редактируемые CMS-страницы и кастомизированная Jazzmin-админка.

Проект рассчитан на локальную разработку без обязательных внешних сервисов: SQLite, локальные `media`-файлы, Django templates и vanilla JS. SMTP, Gunicorn/WhiteNoise и Render-конфигурация подключены для production-сценариев.

---

## Возможности

- **Каталог одежды** - категории, подкатегории, вложенные подкатегории, бренды, поиск, сортировка, фильтры по цене/цвету/размеру/материалу/сезону/стилю.
- **Товарные карточки** - изображения, артикулы `VL-*`, описание, состав, старая цена, скидка, флаги "новинка" и "рекомендуемое".
- **Варианты товаров** - размеры, цвета, SKU и складские остатки для каждого варианта.
- **Корзина** - работает для гостей через сессию и для авторизованных пользователей через связанную корзину; при входе гостевая корзина объединяется с пользовательской.
- **Оформление заказа** - заказ для гостя или пользователя, адрес доставки, способы оплаты, создание аккаунта при checkout, списание остатков.
- **Личный кабинет** - профиль, адреса, история заказов, детали заказа, смена пароля.
- **Избранное** - хранение для авторизованных пользователей и синхронизация гостевых избранных через API.
- **Отзывы** - оценки и тексты отзывов с модерацией через админку.
- **Рассылки** - подписчики, приветственные письма, отписка и отправка newsletter из админки.
- **CMS-страницы** - главная, о магазине, доставка, контакты, возврат, оферта, политика конфиденциальности и редактируемые секции.
- **Админка** - Jazzmin, inline-изображения, варианты товаров, адреса пользователей, статусы заказов, страницы, баннеры и рассылки.
- **Demo seed** - команда создаёт каталог, фильтры, бренды, пользователей, корзины, заказы и CMS-контент.

---

## Стек

| Слой | Технологии |
|---|---|
| Backend | Python 3.11, Django 5.1.4, Django REST Framework 3.15 |
| Admin | django-jazzmin 3.0.1 + кастомный CSS |
| DB | SQLite локально |
| Frontend | Django templates, HTML, CSS, Vanilla JS |
| API | DRF ViewSets/APIView, django-filter, Simple JWT |
| Media | Django `ImageField`, Pillow, локальные `media/` и `seed_data/images/` |
| Static | WhiteNoise, локальные шрифты через `scripts/download_fonts.py` |
| Email | SMTP или Resend backend helper |
| Deploy | Render, Gunicorn, `build.sh`, `render.yaml` |

---

## Быстрый старт

```bash
git clone https://github.com/velour26/velour
cd velour
python -m venv .venv
.venv\Scripts\Activate.ps1      # Windows PowerShell
# source .venv/bin/activate      # Linux/macOS
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_db
python manage.py import_images --replace
python manage.py runserver
```

Открыть сайт: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

Админка: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

> Если `python` не найден, используйте полный путь к интерпретатору активного окружения или установите Python 3.11.

---

## Переменные окружения

Создай `.env` на основе `.env.example` или вручную:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Email через SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-brevo-login@email.com
EMAIL_HOST_PASSWORD=your-brevo-smtp-key
DEFAULT_FROM_EMAIL=VELOUR <noreply@velour.ru>

# CORS, если нужен внешний frontend
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

В `render.yaml` также предусмотрены SMTP-настройки для Yandex/SSL и автоматическая генерация `SECRET_KEY`.

---

## Demo seed

Основная команда:

```bash
python manage.py seed_db
python manage.py import_images --replace
```

Полная очистка demo-данных и повторная заливка:

```bash
python manage.py seed_db --flush
python manage.py import_images --replace
```

Дополнительные утилиты:

```bash
python scripts/download_fonts.py
python scripts/download_wb_images.py
```

Что создаёт `seed_db`:

- настройки сайта VELOUR;
- категории, подкатегории и вложенные подкатегории;
- группы фильтров и опции: цвет, размер, материал, сезон, стиль;
- бренды, включая Befree, Love Republic, LIME, 12 STOREEZ, ZARINA, Zara, H&M, Mango и другие;
- 110+ товаров с артикулами `VL-*`, вариантами, остатками и изображениями-заглушками;
- 2 администратора, 3 менеджера и 20 покупателей;
- адреса покупателей, активные корзины и историю заказов;
- CMS-страницы и баннеры.

Команда `import_images` подтягивает реальные изображения из `seed_data/images/` в `media/products/`.

---

## Демо-доступы

Вход покупателей: `/account/login/`  
Вход менеджеров и админов: `/admin/`

### Покупатели

Пароль для всех покупателей: `User123!`

| Пользователь | Email | Пароль |
|---|---|---|
| `user1` | `user1@example.com` | `User123!` |
| `user2` | `user2@example.com` | `User123!` |
| `user3` | `user3@example.com` | `User123!` |
| `...` | `userN@example.com` | `User123!` |
| `user20` | `user20@example.com` | `User123!` |

### Менеджеры

Пароль для всех менеджеров: `Manager123!`

| Пользователь | Email | Пароль |
|---|---|---|
| `manager1` | `manager1@velour.ru` | `Manager123!` |
| `manager2` | `manager2@velour.ru` | `Manager123!` |
| `manager3` | `manager3@velour.ru` | `Manager123!` |

### Администраторы

Пароль для всех администраторов: `Admin123!`

| Пользователь | Email | Пароль |
|---|---|---|
| `admin1` | `admin1@velour.ru` | `Admin123!` |
| `admin2` | `admin2@velour.ru` | `Admin123!` |

> Demo-пароли нужны только для разработки. Перед production удалите demo-пользователей или смените пароли.

---

## Роли

| Роль | Доступ | Назначение |
|---|---|---|
| Покупатель | `/account/login/`, пользовательские страницы | покупки, корзина, избранное, адреса, история заказов |
| Менеджер | `/admin/` | операционная работа в админке |
| Администратор | `/admin/` | полный доступ к админке и настройкам |

Роль хранится в кастомной модели пользователя `accounts.User`: `customer`, `manager`, `admin`. В seed-данных менеджеры и администраторы получают staff/superuser-доступ.

---

## Основные страницы

| URL | Назначение |
|---|---|
| `/` | Главная страница |
| `/catalog/` | Каталог товаров |
| `/catalog/favorites/` | Избранное |
| `/catalog/<category_slug>/` | Категория каталога |
| `/catalog/<category_slug>/<product_slug>/` | Страница товара |
| `/cart/` | Корзина |
| `/orders/checkout/` | Оформление заказа |
| `/orders/payment/<order_number>/` | Оплата заказа |
| `/orders/success/<order_number>/` | Успешное оформление |
| `/orders/sbp-success/<order_number>/` | Успешная SBP-оплата |
| `/orders/my/` | Мои заказы |
| `/orders/my/<number>/` | Детали заказа |
| `/account/login/` | Вход |
| `/account/register/` | Регистрация |
| `/account/profile/` | Профиль |
| `/account/password-reset/` | Восстановление пароля |
| `/about/` | О магазине |
| `/delivery/` | Доставка |
| `/contacts/` | Контакты |
| `/returns/` | Возврат |
| `/privacy/` | Политика конфиденциальности |
| `/terms/` | Условия / оферта |
| `/newsletter/confirm/<token>/` | Подтверждение подписки |
| `/newsletter/unsubscribe/` | Отписка |
| `/admin/` | Админка |

---

## REST API

| Метод | URL | Доступ | Описание |
|---|---|---|---|
| GET | `/api/categories/` | public | Категории |
| GET | `/api/categories/{slug}/` | public | Деталка категории |
| GET | `/api/products/` | public | Товары, фильтры, поиск, сортировка, пагинация |
| GET | `/api/products/{slug}/` | public | Деталка товара |
| GET | `/api/products/{slug}/reviews/` | public | Отзывы товара |
| POST | `/api/products/{slug}/add_review/` | user | Добавить отзыв |
| GET | `/api/filters/` | public | Группы фильтров и опции |
| GET | `/api/brands/` | public | Бренды |
| GET/DELETE | `/api/cart/` | any | Получить или очистить корзину |
| POST | `/api/cart/add/` | any | Добавить товар в корзину |
| PATCH/DELETE | `/api/cart/items/{item_id}/` | any | Изменить или удалить позицию |
| GET | `/api/orders/` | user | История заказов пользователя |
| POST | `/api/orders/create/` | any | Создать заказ |
| GET | `/api/orders/{number}/` | owner/session | Детали заказа |
| POST | `/api/orders/{number}/cancel/` | user | Отменить заказ |
| POST | `/api/auth/login/` | any | API-вход |
| POST | `/api/auth/logout/` | user | API-выход |
| POST | `/api/auth/register/` | any | API-регистрация |
| GET/PATCH | `/api/auth/profile/` | user | Профиль |
| POST | `/api/auth/change-password/` | user | Смена пароля |
| GET/POST | `/api/auth/addresses/` | user | Адреса |
| GET/PATCH/DELETE | `/api/auth/addresses/{id}/` | user | Адрес |
| GET | `/api/favorites/` | user | Избранные товары |
| GET | `/api/favorites/status/` | user | ID избранных товаров |
| POST | `/api/favorites/{product_id}/` | user | Добавить/убрать избранное |
| GET/POST | `/api/favorites/sync/` | any | Синхронизация гостевого избранного |
| POST | `/api/newsletter/subscribe/` | any | Подписка |
| GET | `/api/newsletter/confirm/{token}/` | any | Подтверждение подписки |
| POST | `/api/newsletter/unsubscribe/` | any | Отписка |

DRF pagination: `PAGE_SIZE = 24`.

---

## Структура проекта

```text
.
├── apps/
│   ├── accounts/       # пользователь, адреса, auth pages
│   ├── api/            # DRF endpoints, serializers, filters, email utils
│   ├── cart/           # корзина и позиции корзины
│   ├── catalog/        # каталог, товары, бренды, фильтры, отзывы, seed commands
│   ├── newsletter/     # подписчики и рассылки
│   ├── orders/         # заказы, позиции, история статусов
│   └── pages/          # главная, CMS-страницы, баннеры, site settings
├── config/             # settings, urls, middleware, wsgi/asgi
├── media/              # uploaded/generated media
├── scripts/            # загрузка шрифтов и изображений
├── seed_data/          # исходные demo-изображения товаров
├── static/             # CSS, JS, images
├── templates/          # HTML и email-шаблоны
├── manage.py
├── requirements.txt
├── build.sh
├── Dockerfile
├── Procfile
└── render.yaml
```

---

## Полезные команды

```bash
# Django
python manage.py runserver
python manage.py check
python manage.py migrate
python manage.py makemigrations
python manage.py seed_db
python manage.py seed_db --flush
python manage.py import_images --replace
python manage.py createsuperuser
python manage.py collectstatic
python manage.py shell

# Assets
python scripts/download_fonts.py
python scripts/download_wb_images.py

# Production-like запуск
gunicorn config.wsgi:application --workers 2 --bind 0.0.0.0:8000 --timeout 120
```

---

## Админка

Админка находится на `/admin/`. В ней редактируются:

- пользователи, роли и адреса;
- категории, подкатегории, бренды и фильтры;
- товары, изображения и варианты;
- отзывы и избранное;
- заказы, позиции заказов и история статусов;
- настройки сайта, CMS-страницы, секции и баннеры;
- подписчики и email-рассылки.

В проекте подключён Jazzmin и `static/css/admin_custom.css`.

---

## Production notes

- Установите сильный `SECRET_KEY`.
- Переведите `DEBUG=False` после проверки production-настроек.
- Настройте `ALLOWED_HOSTS` и домен Render/сервера.
- Выполните `python manage.py collectstatic`.
- Выполните `python manage.py migrate`.
- Запустите `python manage.py seed_db` только если нужны demo-данные.
- Настройте SMTP-переменные для писем восстановления пароля, подтверждений заказа и рассылок.
- Проверьте хранение `media/`: в текущей конфигурации файлы лежат локально в репозитории/файловой системе.
- Смените или удалите demo-пользователей.

На Render сборка выполняется через `build.sh`: установка зависимостей, `collectstatic`, миграции, загрузка шрифтов и seed только при пустой таблице товаров.

---

## Типовые проблемы

### `python` не найден

Установите Python 3.11 или активируйте виртуальное окружение:

```bash
.venv\Scripts\Activate.ps1
```

### В каталоге нет товаров

Проверьте, что выполнены миграции и seed:

```bash
python manage.py migrate
python manage.py seed_db
python manage.py import_images --replace
```

### В товарах нет реальных изображений

Seed создаёт placeholder-изображения. Для загрузки demo-картинок из `seed_data/images/` выполните:

```bash
python manage.py import_images --replace
```

### Не работает вход в админку

Убедитесь, что выполнен seed, затем используйте:

```text
admin1@velour.ru / Admin123!
```

### Не отправляются письма

Проверьте `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`/`EMAIL_USE_SSL`, логин, пароль приложения и `DEFAULT_FROM_EMAIL`.

---

## Лицензия

Проект разработан для учебных и коммерческих целей.
