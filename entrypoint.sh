#!/bin/sh
set -e

# 1. Применяем миграции
echo "Running migrations..."
python manage.py migrate --noinput

# 2. Проверяем переменную RUN_IMPORT
if [ "$RUN_IMPORT" = "true" ]; then
  echo "RUN_IMPORT is true. Starting data import..."

  # Загружаем фикстуру
  echo "Loading fixture seed_data/current_db.json..."
  python manage.py loaddata seed_data/current_db.json --verbosity=2
  
  echo "Import finished successfully."
fi

# 3. Запускаем сервер
echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --workers 2 --bind 0.0.0.0:${PORT:-8000} --timeout 120