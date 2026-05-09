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

# Optional rebuild of ProductImage records from committed media/products files.
if [ "${IMPORT_PRODUCT_IMAGES:-false}" = "true" ]; then
  python manage.py import_images --flat-dir media/products --replace
fi

