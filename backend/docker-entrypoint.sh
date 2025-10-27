#!/bin/bash
set -e

echo "Starting ReleaseDrop Backend..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is ready!"

# Run any pending migrations (if needed)
# python migrate_phase2.py
# python add_plex_columns.py

echo "Backend initialization complete!"
echo "Starting ReleaseDrop API..."

# Execute the CMD
exec "$@"
