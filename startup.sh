#!/usr/bin/env bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_groups
python manage.py seed_admin
exec gunicorn PetShelterDjango.wsgi --bind 0.0.0.0:${PORT:-8000}
