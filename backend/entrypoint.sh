#!/bin/sh
python manage.py collectstatic --noinput
python manage.py migrate

gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --reload --access-logfile /app/logs/django.log --error-logfile /app/logs/django.log