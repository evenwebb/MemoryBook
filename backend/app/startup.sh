#!/bin/bash
# Startup script for backend

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until PGPASSWORD=memorybook psql -h postgres -U memorybook -d memorybook -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is ready!"

# Initialize database with default categories
echo "Initializing database..."
python -m app.core.init_db || echo "Database initialization skipped or failed"

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

