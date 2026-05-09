#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput

if [ "${RUN_IMPORT:-false}" = "true" ]; then
  echo "RUN_IMPORT=true detected, loading fixture..."
  python manage.py loaddata seed_data/current_db.json --verbosity=2
fi

