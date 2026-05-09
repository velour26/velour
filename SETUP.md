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
Файл `.env.example` уже создан с настройками для разработки (SQLite + email в консоль).

### 4. Скачать локальные шрифты и картинки
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
- 110 товара с вариантами (484 шт.) и плейсхолдер-изображениями
- Категории / подкатегории / фильтры из БД
- 2 admin, 3 manager, 20 customer
- Историю заказов и активные корзины для каждого пользователя
- CMS-страницы (главная, о нас, доставка, контакты, возврат, оферта, политика)

### 7. Запустить сервер
```bash
python manage.py runserver
```
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