# VELOUR — Инструкция по запуску

## Локальный запуск

### 1. Создать виртуальное окружение
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 2. Установить зависимости
```bash
pip install -r requirements.txt
```

### 3. Настроить переменные окружения
Файл `.env` уже создан с настройками для разработки (SQLite + email в консоль).
При необходимости отредактируйте его.

### 4. Скачать локальные шрифты
```bash
python scripts/download_fonts.py
python scripts/download_wb_images.py
```

### 5. Применить миграции
```bash
python manage.py makemigrations accounts catalog cart orders pages newsletter
python manage.py migrate
```

### 6. Заполнить БД тестовыми данными
```bash
python manage.py seed_db
python manage.py import_images --replace
```
Создаст:
- 74 товара с вариантами (484 шт.) и плейсхолдер-изображениями
- Категории / подкатегории / фильтры из БД
- 2 admin, 3 manager, 20 customer
- Историю заказов и активные корзины для каждого пользователя
- CMS-страницы (главная, о нас, доставка, контакты, возврат, оферта, политика)

### 7. Запустить сервер
```bash
python manage.py runserver
```

Сайт: http://127.0.0.1:8000  
Админка: http://127.0.0.1:8000/admin/

---

## Учётные записи после seed_db

| Роль    | Email               | Пароль      |
|---------|---------------------|-------------|
| Admin 1 | admin1@velour.ru    | Admin123!   |
| Admin 2 | admin2@velour.ru    | Admin123!   |
| Manager | manager1@velour.ru  | Manager123! |
| Manager | manager2@velour.ru  | Manager123! |
| Manager | manager3@velour.ru  | Manager123! |
| User    | user1@example.com   | User123!    |
| User    | user2@example.com   | User123!    |
| ...     | userN@example.com   | User123!    |

---

## Деплой на Render

> **База данных**: SQLite-файл.  

1. Создать репозиторий на GitHub и запушить код:
```bash
git init
git add .
git commit -m "Initial VELOUR project"
git remote add origin https://github.com/YOUR/velour.git
git push -u origin main
```

2. На [render.com](https://render.com):
   - New → **Web Service** → подключить репозиторий
   - Build Command: `./build.sh`
   - Start Command: `gunicorn config.wsgi:application --workers 2 --bind 0.0.0.0:$PORT --timeout 120`

---

## Структура проекта

```
velour/
├── apps/
│   ├── accounts/    # Пользователи, роли (customer/manager/admin), адреса
│   ├── catalog/     # Товары, категории, фильтры, бренды, отзывы
│   ├── cart/        # Корзина (guest + auth, session merge)
│   ├── orders/      # Заказы, статусы, история
│   ├── pages/       # CMS: страницы, секции, баннеры, настройки сайта
│   ├── newsletter/  # Подписчики, рассылки
│   └── api/         # DRF: сериализаторы, вьюсеты, роутеры
├── config/          # settings.py, urls.py, wsgi.py
├── static/          # CSS (variables/base/header/footer/catalog/pages), JS, fonts
├── templates/       # Все HTML (base, includes, pages, catalog, cart, orders, account, email)
├── scripts/         # download_fonts.py
├── seed_data/       # images/ (папка для изображений товаров)
├── render.yaml      # Render деплой-конфиг
├── build.sh         # Скрипт сборки для Render
└── SETUP.md         # Эта инструкция
```
