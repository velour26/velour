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

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--workers", "2", "--bind", "0.0.0.0:8000", "--timeout", "120"]
