FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install whitenoise

RUN mkdir -p /usr/src/app/static /usr/src/app/staticfiles /usr/src/app/media

COPY . .

RUN chmod -R 755 /usr/src/app/static /usr/src/app/staticfiles /usr/src/app/media

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]