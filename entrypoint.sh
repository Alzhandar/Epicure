#!/bin/bash

echo "Waiting for postgres..."
python -c "
import sys, time, psycopg2;
while True:
    try:
        psycopg2.connect(
            dbname='${DB_NAME}',
            user='${DB_USER}',
            password='${DB_PASSWORD}',
            host='${DB_HOST}',
            port='${DB_PORT}'
        );
        print('PostgreSQL is available');
        break;
    except Exception as e:
        print('PostgreSQL is unavailable - sleeping');
        print(f'Error: {e}');
        time.sleep(1);
"

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Setting up media directory..."
mkdir -p /usr/src/app/media
chmod -R 777 /usr/src/app/media

echo "Starting Gunicorn..."
gunicorn core.wsgi:application --bind 0.0.0.0:8000