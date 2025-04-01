python manage.py migrate

python manage.py collectstatic --noinput

exec gunicorn --bind 0.0.0.0:8000 --workers 3 main.wsgi:application