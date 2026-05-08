#!/bin/sh
set -e

python manage.py migrate --noinput

python manage.py shell -c "
from apps.catalog.models import Product
if not Product.objects.exists():
    from django.core.management import call_command
    call_command('seed_db')
    print('Database seeded.')
else:
    print('Database already has data, skipping seed.')
"

exec gunicorn config.wsgi:application --workers 2 --bind 0.0.0.0:8000 --timeout 120
