#!/bin/bash

echo "Waiting for postgres..."

until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "PostgreSQL недоступен - ждем..."
  sleep 2
done

echo "PostgreSQL запущен"

python manage.py makemigrations

python manage.py migrate
python manage.py collectstatic --noinput

PORT=${PORT:-8000}
echo "Starting server on port $PORT"

exec gunicorn --bind 0.0.0.0:$PORT --workers 3 core.wsgi:application