RUN echo '#!/bin/bash \n\
echo "Waiting for postgres..." \n\
python -c "\
import sys, time, psycopg2; \
while True: \
    try: \
        psycopg2.connect(dbname=\"$DB_NAME\", user=\"$DB_USER\", password=\"$DB_PASSWORD\", host=\"$DB_HOST\", port=\"$DB_PORT\"); \
        print(\"PostgreSQL is available\"); \
        break; \
    except psycopg2.OperationalError: \
        print(\"PostgreSQL is unavailable - sleeping\"); \
        time.sleep(1); \
" \
python manage.py migrate \n\
python manage.py collectstatic --noinput \n\
\n\
# Запуск Gunicorn \n\
gunicorn core.wsgi:application --bind 0.0.0.0:8000 \n\
' > /app/entrypoint.sh