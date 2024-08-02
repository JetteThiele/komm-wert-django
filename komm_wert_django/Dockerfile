# Basis-Image
FROM python:3.9-slim

# Arbeitsverzeichnis erstellen und setzen
RUN mkdir /app
WORKDIR /app

# Abhängigkeiten kopieren
COPY requirements.txt /app/
COPY gunicorn_config.py /app/
# Abhängigkeiten installieren
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY . /app/
COPY .env /app/

# Umgebungsvariablen setzen (falls notwendig)
ENV DJANGO_SETTINGS_MODULE="komm_wert_django.settings"
ENV PYTHONUNBUFFERED=1

# Sammle statische Dateien
RUN python manage.py collectstatic --noinput

# Port freigeben
EXPOSE 8000

# Startbefehl setzen
CMD ["gunicorn", "--config", "gunicorn_config.py", "komm_wert_django.wsgi:application"]