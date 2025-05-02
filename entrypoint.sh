#!/bin/bash

echo "Waiting for postgres..."
while ! nc -z $DB_HOST $DB_PORT; do
  echo "PostgreSQL недоступен - ждем..."
  sleep 2
done

echo "PostgreSQL запущен"

echo "Создание миграций..."
python manage.py makemigrations

echo "Применение миграций..."
python manage.py migrate

echo "Сборка статических файлов..."
python manage.py collectstatic --noinput

echo "Запуск сервера..."
gunicorn core.wsgi:application --bind 0.0.0.0:8000