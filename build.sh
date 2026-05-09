#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput

if [ "${RUN_IMPORT:-false}" = "true" ]; then
  python manage.py import_db --flush --images
fi

