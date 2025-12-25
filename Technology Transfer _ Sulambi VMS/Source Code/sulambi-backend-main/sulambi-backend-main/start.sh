#!/bin/bash
# Startup script for Render deployment

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Initialize database if it doesn't exist
# Check if we're using PostgreSQL (production) or SQLite
if [ -n "$DATABASE_URL" ]; then
  echo "Using PostgreSQL database..."
  # For PostgreSQL, we'll let the app handle initialization
  # The tableInitializer should work with PostgreSQL if we update it
  python server.py --init || echo "Database may already be initialized"
else
  echo "Using SQLite database..."
  # For SQLite, check if database exists
  if [ ! -f "$DB_PATH" ]; then
    echo "Initializing database..."
    python server.py --init
  else
    echo "Database already exists, skipping initialization"
  fi
fi

# Start the server with Gunicorn
echo "Starting Gunicorn server..."
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 server:app

