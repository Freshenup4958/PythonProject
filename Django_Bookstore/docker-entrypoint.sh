#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."

python - <<'PY'
import os
import time
import psycopg

host = os.getenv("POSTGRES_HOST", "db")
port = os.getenv("POSTGRES_PORT", "5432")
dbname = os.getenv("POSTGRES_DB", "bookstore")
user = os.getenv("POSTGRES_USER", "bookstore_user")
password = os.getenv("POSTGRES_PASSWORD", "bookstore_password")

while True:
    try:
        connection = psycopg.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
        )
        connection.close()
        print("PostgreSQL is ready.")
        break
    except psycopg.OperationalError:
        print("PostgreSQL is unavailable - waiting...")
        time.sleep(2)
PY

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Django..."

exec "$@"