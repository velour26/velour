#!/bin/sh
set -e

python manage.py migrate --noinput

exec gunicorn config.wsgi:application --workers 2 --bind 0.0.0.0:${PORT:-8000} --timeout 120
