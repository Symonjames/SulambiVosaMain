#!/bin/bash
# Startup script for Render deployment

# Create uploads directory if it doesn't exist
mkdir -p uploads

# PostgreSQL is required in production.
if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is required (PostgreSQL only)." >&2
  exit 1
fi
echo "Using PostgreSQL database..."
python server.py --init || echo "Database may already be initialized"

# Start the server with Gunicorn
# Short TMPDIR avoids "AF_UNIX path too long" on hosts with very long cwd paths (e.g. Render).
export TMPDIR="${TMPDIR:-/tmp}"
echo "Starting Gunicorn server..."
gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 2 --timeout 120 server:app

