# Backend Dockerfile
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y gcc libpq-dev --no-install-recommends \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# copy and install python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# copy app
COPY . /app

# make scripts executable
RUN chmod +x /app/scripts/start_with_migrations.sh || true

# expose port
EXPOSE 8000

# default command: run migrations then start the app
CMD ["/app/scripts/start_with_migrations.sh"]
