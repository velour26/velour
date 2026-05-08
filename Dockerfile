FROM python:3.11.0-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

RUN python scripts/download_fonts.py

RUN chmod +x ./entrypoint.sh

EXPOSE 8000

ENV PYTHON_VERSION=3.11.0
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV DEBUG=True
ENV ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
ENV PORT=8000

ENTRYPOINT ["./entrypoint.sh"]
