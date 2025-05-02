FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE core.settings

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN mkdir -p /app/staticfiles /app/media

RUN echo '#!/bin/bash \n\
echo "Waiting for postgres..." \n\
while ! nc -z $DB_HOST $DB_PORT; do \n\
  sleep 1 \n\
done \n\
echo "PostgreSQL started" \n\
\n\
python manage.py migrate \n\
python manage.py collectstatic --noinput \n\
\n\
# Запуск Gunicorn \n\
gunicorn core.wsgi:application --bind 0.0.0.0:8000 \n\
' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]