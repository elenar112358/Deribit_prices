#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."

until pg_isready \
    -h "$POSTGRES_HOST" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB"
do
    sleep 1
done

echo "PostgreSQL is ready."

echo "Applying migrations..."
alembic upgrade head

echo "Starting application processes..."
exec supervisord -n -c /app/docker/supervisord.conf
