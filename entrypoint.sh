#!/bin/sh

echo "Setting DJANGO_SETTINGS_MODULE..."
export DJANGO_SETTINGS_MODULE=config.settings.development

echo "Compiling translations..."
python manage.py compilemessages

echo "Applying migrations..."
python manage.py migrate

echo "Waiting a few seconds for migrations to settle..."
sleep 5  # Allow database changes to be fully applied

echo "Checking superuser..."
python -c "
import django
django.setup()
from django.contrib.auth import get_user_model
from django.db import IntegrityError
try:
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        print('Creating superuser...')
        User.objects.create_superuser('admin', 'jamshidiyounes92@gmail.com', 'admin@1234')
    else:
        print('Superuser already exists.')
except Exception as e:
    print('Error while creating superuser:', e)
"

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000