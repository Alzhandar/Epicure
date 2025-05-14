FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DATABASE_ENGINE=django.db.backends.postgresql

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir whitenoise psycopg2-binary python-dotenv gunicorn

RUN mkdir -p /usr/src/app/static /usr/src/app/staticfiles /usr/src/app/media

COPY . .

RUN sed -i 's/\r$//' /usr/src/app/entrypoint.sh && \
    chmod +x /usr/src/app/entrypoint.sh

EXPOSE 8000

CMD ["/usr/src/app/entrypoint.sh"]