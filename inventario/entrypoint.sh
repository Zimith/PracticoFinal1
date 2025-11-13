#!/bin/sh
set -e

# Apply database migrations and collect static files
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput
python manage.py setup_groups || true
python manage.py collectstatic --noinput --clear

exec "$@"
