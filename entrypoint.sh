#!/bin/bash

echo "Waiting for postgres..."

until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "PostgreSQL недоступен - ждем..."
  sleep 2
done

echo "PostgreSQL запущен"

python manage.py migrate
python manage.py collectstatic --noinput

exec gunicorn core.wsgi:application --bind 0.0.0.0:8000