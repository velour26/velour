# PostgreSQL migration on Render

Инструкция для перехода VELOUR с локального SQLite на Render PostgreSQL и переноса текущих данных.

## 1. Что уже настроено в проекте

- `config/settings.py` читает `DATABASE_URL`.
- Если `DATABASE_URL` не задан, локально используется `db.sqlite3`.
- В `requirements.txt` добавлен `psycopg2-binary`.
- `build.sh` умеет загружать fixture из переменной `DJANGO_LOAD_FIXTURE`.
- `build.sh` умеет пересобирать `ProductImage` из `media/products` при `IMPORT_PRODUCT_IMAGES=true`.
- `render.yaml` содержит env vars `DATABASE_URL`, `DJANGO_LOAD_FIXTURE` и `IMPORT_PRODUCT_IMAGES`.

## 2. Создать PostgreSQL на Render

1. Render Dashboard -> `New` -> `Postgres`.
2. Создайте базу в том же регионе, где web service.
3. Откройте базу -> `Connect` / `Info`.
4. Скопируйте `Internal Database URL`.

## 3. Подключить базу к web service

В Render web service `velour` -> `Environment`:

```env
DATABASE_URL=<Internal Database URL>
SEED_DEMO_DATA=false
IMPORT_PRODUCT_IMAGES=true
```

`SEED_DEMO_DATA=false` нужен на время переноса, чтобы пустая PostgreSQL база не заполнилась demo seed до импорта текущей БД.
`IMPORT_PRODUCT_IMAGES=true` пересобирает связи `ProductImage` по файлам `media/products/ARTICLE_*`, если после переноса БД картинки должны совпадать с артикулами сайта.

## 4. Выгрузить текущую SQLite БД в fixture

На машине, где работает Python проекта:

```bash
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude contenttypes \
  --exclude auth.permission \
  --indent 2 \
  -o seed_data/current_db.json
```

На Windows PowerShell:

```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

python manage.py dumpdata `
  --natural-foreign `
  --natural-primary `
  --exclude contenttypes `
  --exclude auth.permission `
  --indent 2 `
  -o seed_data/current_db.json
```

Если без этих переменных появляется ошибка вида:

```text
CommandError: Unable to serialize database: 'charmap' codec can't encode character '\u20bd'
```

значит Python пытается записать JSON в Windows-кодировке вместо UTF-8. Повторите команду в том же PowerShell-окне после установки `PYTHONUTF8` и `PYTHONIOENCODING`, как показано выше.

Проверьте, что файл появился:

```bash
python manage.py shell -c "import json; print(len(json.load(open('seed_data/current_db.json', encoding='utf-8'))))"
```

## 5. Загрузить fixture на Render при деплое

Закоммитьте `seed_data/current_db.json` и задайте в Render:

```env
DJANGO_LOAD_FIXTURE=seed_data/current_db.json
SEED_DEMO_DATA=false
```

После deploy `build.sh` выполнит:

```bash
python manage.py migrate --noinput
python manage.py loaddata seed_data/current_db.json
python manage.py import_images --flat-dir media/products --replace
```

## 6. После успешного импорта

Чтобы fixture не загружался повторно на каждом deploy:

1. Удалите env var `DJANGO_LOAD_FIXTURE` или оставьте пустым.
2. Оставьте `DATABASE_URL`.
3. `IMPORT_PRODUCT_IMAGES` можно выключить после проверки картинок или оставить `true`, если связи нужно гарантированно пересобирать на каждом deploy.
4. `SEED_DEMO_DATA` можно оставить `false`, если production уже содержит реальные данные.

## 7. Проверка

Откройте:

- `/admin/`
- `/catalog/`
- `/api/products/`
- `/account/login/`

В Django shell на Render можно проверить:

```bash
python manage.py shell -c "from apps.catalog.models import Product; from django.contrib.auth import get_user_model; print(Product.objects.count(), get_user_model().objects.count())"
```

## 8. Если база уже случайно заполнилась seed-данными

Самый чистый вариант для первого переноса:

1. Создать новую пустую PostgreSQL базу на Render.
2. Обновить `DATABASE_URL`.
3. Задать `DJANGO_LOAD_FIXTURE=seed_data/current_db.json`.
4. Задать `SEED_DEMO_DATA=false`.
5. При необходимости задать `IMPORT_PRODUCT_IMAGES=true`.
6. Задеплоить заново.

Не импортируйте fixture поверх уже заполненной базы, если не уверены, что primary keys и уникальные поля не конфликтуют.
