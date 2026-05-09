#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Download fonts locally
python scripts/download_fonts.py

# Optional one-time data import from a committed Django fixture.
if [ -n "$DJANGO_LOAD_FIXTURE" ]; then
  python manage.py loaddata "$DJANGO_LOAD_FIXTURE"
fi

# Seed DB only if products table is empty and demo seed is not disabled.
python manage.py shell -c "
import os
from apps.catalog.models import Product
if os.environ.get('SEED_DEMO_DATA', 'true').lower() in ('0', 'false', 'no'):
    print('Demo seed disabled.')
elif not Product.objects.exists():
    from django.core.management import call_command
    call_command('seed_db')
    print('Database seeded.')
else:
    print('Database already has data, skipping seed.')
"
