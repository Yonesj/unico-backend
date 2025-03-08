#!/bin/sh

echo "Waiting for database..."
python manage.py migrate
python manage.py collectstatic --noinput

exec "$@"
