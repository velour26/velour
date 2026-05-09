# VELOUR — интернет-магазин одежды

VELOUR — полнофункциональный интернет-магазин одежды на Django 4.2 и Django REST Framework. Каталог с фильтрами, корзина, оформление заказов, личный кабинет, избранное, подписка на рассылку, SBP-оплата, Jazzmin-админка.

Проект рассчитан на локальную разработку без внешних обязательных сервисов: SQLite, локальные media-файлы. Yandex SMTP подключается опционально для отправки писем. PostgreSQL и S3 — для production на Render.

---

## Возможности

- **Каталог товаров** — категории, подкатегории, фильтры, поиск, сортировка, карточки с изображениями, sale-бейджи, новинки.
- **Страница товара** — галерея, выбор размера и цвета, отзывы, похожие товары, QR-код и кнопка «Поделиться».
- **Корзина и избранное** — работают для гостей через `localStorage` + Django session cache, для авторизованных — через API + backend.
- **Оформление заказа** — наличными при получении, СБП (QR-код с автопроверкой статуса), банковская карта (симуляция).
- **Личный кабинет** — профиль, адреса, история заказов, смена пароля.
- **Админка** — кастомизированная Jazzmin-админка с фильтрами и навигацией.
- **Email** — подтверждение подписки, заказ, восстановление пароля, приветствие.

---

## Стек

| Слой | Технологии |
|---|---|
| Backend | Python 3.11+, Django 4.2, DRF 3.15 |
| Admin | django-jazzmin 3.0 |
| DB | SQLite локально, PostgreSQL через `DATABASE_URL` |
| Frontend | Django templates, HTML, CSS, Vanilla JS |
| Media | Django `ImageField`, локальные demo-файлы |
| Email | Yandex SMTP (порт 587, TLS) |

---

## Быстрый старт

```bash
git clone <url-репозитория>
cd velour
python -m venv .venv
.venv\Scripts\Activate.ps1      # Windows PowerShell
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_db
python manage.py runserver
```

Открыть сайт: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

Админка: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Переменные окружения

Создай `.env` на основе `.env.example` или вручную:

```env
SECRET_KEY=dev-secret-key-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Production DB
# DATABASE_URL=postgres://user:password@host:5432/dbname

# Email (Yandex)
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@yandex.ru
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=VELOUR <noreply@velour.ru>

# Render/production
# USE_S3_MEDIA=True
# AWS_STORAGE_BUCKET_NAME=
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_S3_REGION_NAME=eu-central-1
# AWS_S3_ENDPOINT_URL=
```

---

## Демо-доступы

Вход покупателей: `/account/login/`
Вход администраторов: `/admin/`

### Покупатели (20 пользователей)

Пароль для всех покупателей: `User123!`

| Email | Пароль |
|---|---|
| `user1@example.com` … `user20@example.com` | `User123!` |

### Менеджеры (3 пользователя)

Пароль для всех менеджеров: `Admin123!`

| Email | Пароль |
|---|---|
| `manager1@velour.ru` … `manager3@velour.ru` | `Admin123!` |

### Администраторы (2 пользователя)

| Email | Пароль |
|---|---|
| `admin1@velour.ru`, `admin2@velour.ru` | `Admin123!` |

---

## Основные страницы

| URL | Назначение |
|---|---|
| `/` | Главная страница |
| `/catalog/` | Каталог с фильтрами и сортировкой |
| `/catalog/<category>/` | Категория |
| `/catalog/<category>/<product>/` | Страница товара |
| `/cart/` | Корзина |
| `/orders/checkout/` | Оформление заказа |
| `/orders/payment/<number>/` | Оплата (СБП / карта) |
| `/orders/success/<number>/` | Успешный заказ |
| `/orders/sbp-success/<number>/` | Подтверждение СБП (QR-сканирование) |
| `/catalog/favorites/` | Избранное |
| `/account/login/` | Вход |
| `/account/register/` | Регистрация |
| `/account/profile/` | Профиль покупателя |
| `/orders/my/` | Мои заказы |
| `/about/` | О нас |
| `/delivery/` | Доставка и оплата |
| `/contacts/` | Контакты |
| `/admin/` | Админка |

---

## REST API

| Метод | URL | Доступ | Описание |
|---|---|---|---|
| GET | `/api/products/` | public | Товары, поиск, фильтры, сортировка, пагинация |
| GET | `/api/categories/` | public | Категории |
| GET | `/api/filters/` | public | Схема фильтров каталога |
| GET | `/api/brands/` | public | Бренды |
| GET/POST | `/api/cart/` | any | Корзина |
| GET/POST | `/api/cart/add/` | any | Добавить товар |
| PATCH/DELETE | `/api/cart/items/<id>/` | any | Обновить/удалить позицию |
| POST | `/api/orders/create/` | any | Создать заказ |
| GET | `/api/orders/<number>/` | any | Детали заказа (гости — по session_key) |
| POST | `/api/orders/<number>/cancel/` | user | Отменить заказ |
| GET/POST | `/api/favorites/` | user | Избранное |
| POST | `/api/favorites/<id>/` | user | Добавить/убрать из избранного |
| GET | `/api/favorites/status/` | user | Статус избранного |
| GET/POST | `/api/favorites/sync/` | any | Синхронизация избранного гостя (session cache) |
| POST | `/api/auth/login/` | any | Вход |
| POST | `/api/auth/logout/` | any | Выход |
| POST | `/api/auth/register/` | any | Регистрация |
| GET/POST | `/api/auth/profile/` | user | Профиль |
| POST | `/api/auth/change-password/` | user | Смена пароля |
| GET/POST | `/api/auth/addresses/` | user | Адреса |
| PATCH/DELETE | `/api/auth/addresses/<id>/` | user | Адрес |
| POST | `/api/newsletter/subscribe/` | any | Подписка |
| GET | `/api/newsletter/confirm/<token>/` | any | Подтверждение подписки |
| POST | `/api/newsletter/unsubscribe/` | any | Отписка |

---

## Структура проекта

```text
velour/
├── apps/
│   ├── accounts/       # Пользователи, авторизация, адреса
│   ├── api/            # REST API (catalog, cart, orders, accounts, favorites, newsletter)
│   ├── cart/           # Модель корзины и сессии
│   ├── catalog/        # Каталог: товары, категории, фильтры, избранное, отзывы
│   ├── newsletter/     # Подписка на рассылку
│   ├── orders/         # Заказы, оплата, SBP, success-страницы
│   └── pages/          # Главная, о нас, доставка, контакты
├── config/             # Django settings, urls, middleware, wsgi, asgi
├── media/              # Изображения товаров, категорий, брендов
├── scripts/            # Утилиты (загрузка шрифтов)
├── seed_data/          # Экспорт/импорт БД, изображения для импорта
├── static/
│   ├── css/
│   │   ├── base.css        # Базовые стили, переменные, кнопки, формы, модалки
│   │   ├── catalog.css     # Карточки, сетка, фильтры, каталог
│   │   ├── header.css     # Header, навигация, mobile nav
│   │   ├── footer.css     # Footer
│   │   ├── pages.css      # Home, product detail, cart, checkout, account, orders
│   │   ├── admin_custom.css
│   │   ├── fonts.css
│   │   └── variables.css  # CSS-переменные (цвета, шрифты, spacing)
│   └── js/
│       ├── main.js         # Общие: header search, qty controls, toasts, fav badge
│       ├── catalog.js      # Каталог: фильтры, AJAX загрузка, избранное
│       ├── cart.js          # Корзина: обновление, удаление, пересчёт
│       ├── checkout.js     # Checkout: валидация, создание заказа
│       └── account.js      # Профиль: сохранение, заказы, адреса
├── templates/
│   ├── account/          # login, register, profile
│   ├── catalog/          # catalog, product_detail, favorites
│   ├── cart/             # cart
│   ├── email/            # Письма: заказ, приветствие, подписка, сброс пароля
│   ├── includes/         # header, footer, product_card
│   ├── orders/           # checkout, payment, success, sbp_success, my_orders, order_detail
│   ├── pages/            # home, page (о нас, доставка, контакты), unsubsribe, newsletter
│   └── base.html
├── .env.example
├── db.sqlite3
├── manage.py
└── requirements.txt
```

---

## Ключевые механизмы

### Избранное для гостей

Гости хранят избранное в `localStorage` (`velour_favorites`). При каждом изменении набор синхронизируется с Django session cache через `/api/favorites/sync/` (30-дневный TTL). При авторизации избранное берётся из backend DB.

### SBP-оплата

1. QR-код содержит URL `/orders/sbp-success/<number>/`.
2. Страница `/orders/payment/<number>/` поллит `/api/orders/<number>/` каждые 2 секунды.
3. При сканировании телефона телефон открывает `/orders/sbp-success/<number>/`, сервер сразу помечает заказ как оплаченный.
4. Desktop видит `payment_status: paid` → автопереход на success.

### Заказы гостей

Гости идентифицируются по `session_key`. При создании заказа поле `session_key` сохраняется. Views и API lookup сначала ищут по `session_key`, потом по `guest_email`.

### Email

Все письма отправляются через `threading.Thread` (async) для предотвращения timeout gunicorn workers.

---

## Экспорт и импорт базы данных

Для локальной разработки данные можно выгрузить в JSON и загрузить на production (PostgreSQL на Render).

### Экспорт

```bash
# Только JSON (пути к файлам сохраняются как строки)
python manage.py export_db

# JSON + копирование реальных изображений в seed_data/images/
python manage.py export_db --images
```

Результат: `seed_data/current_db.json` (+ `seed_data/images/` при `--images`).

### Импорт

```bash
# Только данные (изображения остаются как пути в JSON)
python manage.py import_db

# Данные + копирование файлов из seed_data/images/ в MEDIA_ROOT
python manage.py import_db --images
```

Опция `--flush` удаляет все существующие данные перед загрузкой:

```bash
python manage.py import_db --flush --images
```

Пароли пользователей при импорте НЕ сохраняются. Все пользователи получают:
- `Admin123!` — администраторы и менеджеры
- `User123!` — покупатели

На Render: Build Command запускает импорт через переменную окружения:

```bash
python manage.py migrate && RUN_IMPORT=true python manage.py import_db --flush --images && python manage.py collectstatic --noinput
```

`RUN_IMPORT=true` запускает импорт. На всех последующих деплоях импорт НЕ сработает — команда проверяет значение переменной.

### Порядок загрузки

Импорт загружает модели в порядке зависимостей: SiteSettings → FilterGroups → Categories → Products → Images → Variants → Users → Addresses → Orders → Carts → Pages → Subscribers → Favorites. FK/M2M связи пересчитываются по old pk → new pk.

---

## Полезные команды

```bash
# Django
python manage.py runserver
python manage.py check
python manage.py migrate
python manage.py makemigrations
python manage.py createsuperuser
python manage.py seed_db
python manage.py seed_db --flush
python manage.py collectstatic
python manage.py shell

# Data export / import
python manage.py export_db
python manage.py export_db --images
python manage.py import_db
python manage.py import_db --flush --images

# Production
gunicorn config.wsgi:application --workers 2 --bind 0.0.0.0:8000 --timeout 120
```

---

## Production notes

- Установите `DEBUG=False`.
- Задайте сильный `SECRET_KEY`.
- Настройте `ALLOWED_HOSTS` и `CSRF_TRUSTED_ORIGINS`.
- Подключите PostgreSQL через `DATABASE_URL`, если SQLite недостаточно.
- Настройте Yandex SMTP для отправки писем.
- Выполните `python manage.py collectstatic`.
- Смените или удалите demo-пользователей.

---

## Типовые проблемы

### На Render нет картинок
Render free использует ephemeral filesystem: загруженные во время работы файлы пропадают после redeploy/restart. Для production-сценария подключите внешний bucket через `USE_S3_MEDIA=True`.

### Gmail SMTP не работает на Render
Render блокирует исходящие соединения на порту 465. Используйте Yandex SMTP с портом 587 и `EMAIL_USE_TLS=True`.

### Избранное не сохраняется между устройствами
Для гостей избранное хранится в localStorage браузера и session cache сервера. При смене браузера/устройства избранное не сохраняется. Авторизованные пользователи видят избранное везде.

### `import_db` выдаёт ошибку с изображениями
При импорте в PostgreSQL изображения сохраняются как строки-пути. Если нужны реальные файлы, сначала экспортируйте с `--images`, скопируйте `seed_data/images/` в репозиторий, и импортируйте с `--images`.

---

## Лицензия

Проект разработан для учебных и коммерческих целей.