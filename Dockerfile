FROM python:3.11-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn whitenoise psycopg2-binary

RUN mkdir -p /usr/src/app/static /usr/src/app/staticfiles /usr/src/app/media

COPY . .

RUN chmod -R 755 /usr/src/app/static /usr/src/app/staticfiles /usr/src/app/media
RUN chmod +x /usr/src/app/entrypoint.sh

EXPOSE $PORT

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]