FROM python:3.12-slim

# Установка рабочей директории
WORKDIR /app

# Установка переменных окружения для Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE core.settings

# Установка необходимых системных пакетов
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

# Права на выполнение
RUN chmod +x /app/entrypoint.sh

# Открываем порт для приложения
EXPOSE 8000

# Используем готовый файл entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]