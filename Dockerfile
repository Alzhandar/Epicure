FROM python:3.12-slim

# Установка рабочей директории
WORKDIR /app

# Установка переменных окружения для Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE core.settings

# Установка необходимых системных пакетов
# netcat-traditional добавлен для проверки соединений
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . /app/

# Создание директорий для статики и медиа
RUN mkdir -p /app/staticfiles /app/media

# Скрипт для запуска
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

# Открываем порт для приложения
EXPOSE 8000

# Основной скрипт для запуска
ENTRYPOINT ["/app/entrypoint.sh"]