#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Download fonts locally
python scripts/download_fonts.py

# Seed DB only if products table is empty
python manage.py shell -c "
from apps.catalog.models import Product
if not Product.objects.exists():
    from django.core.management import call_command
    call_command('seed_db')
    print('Database seeded.')
else:
    print('Database already has data, skipping seed.')
"
