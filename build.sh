#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput

echo ">>> RUN_IMPORT=${RUN_IMPORT:-unset}"
echo ">>> CI=${CI:-unset}"

if [ "${RUN_IMPORT:-false}" = "true" ]; then
  echo "RUN_IMPORT=true detected, loading fixture..."
  mkdir -p media/products
  cp -r seed_data/images/* media/products/ 2>/dev/null || true
  python manage.py loaddata seed_data/current_db.json --verbosity=2
fi

