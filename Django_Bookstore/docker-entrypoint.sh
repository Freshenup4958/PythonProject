#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."

python - <<'PY'
import os
import time
import psycopg


database_url = os.getenv("DATABASE_URL")

while True:
    try:
        if database_url:
            connection = psycopg.connect(database_url)
        else:
            connection = psycopg.connect(
                host=os.getenv("POSTGRES_HOST", "db"),
                port=os.getenv("POSTGRES_PORT", "5432"),
                dbname=os.getenv("POSTGRES_DB", "bookstore"),
                user=os.getenv("POSTGRES_USER", "bookstore_user"),
                password=os.getenv("POSTGRES_PASSWORD", "bookstore_password"),
            )

        connection.close()
        print("PostgreSQL is ready.")
        break
    except psycopg.OperationalError:
        print("PostgreSQL is unavailable - waiting...")
        time.sleep(2)
PY

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
    echo "Applying migrations..."
    python manage.py migrate --noinput

    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "Starting application..."
exec "$@"
