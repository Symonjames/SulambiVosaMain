from dotenv import load_dotenv
import re
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL DSN

def is_postgresql_url(url: str | None) -> bool:
  """
  Render/Heroku-style Postgres URLs may be either:
  - postgresql://...
  - postgres://...
  Treat both as PostgreSQL.
  """
  if not url:
    return False
  return url.startswith("postgresql://") or url.startswith("postgres://")

IS_POSTGRESQL = is_postgresql_url(DATABASE_URL)

def quote_identifier(identifier):
    """Normalize identifiers for PostgreSQL (unquoted lowercase)."""
    return identifier.lower()

def table_name_for_query(identifier):
    """
    PostgreSQL folds unquoted identifiers to lowercase. Use lowercase in SQL
    so we match typical Render/migrated schemas without an extra DB round-trip.
    (Avoids opening a connection per table on cold start — that amplified timeouts.)
    """
    key = str(identifier or "")
    if not key:
        return key
    return key.lower()

def convert_placeholders(query):
    """Convert qmark placeholders to psycopg2 placeholders."""
    return query.replace('?', '%s')

def is_postgresql_connection(conn):
    """Check if connection is PostgreSQL by checking connection type"""
    try:
        # Check if it's a psycopg2 connection
        return hasattr(conn, 'server_version') or type(conn).__module__.startswith('psycopg2')
    except:
        return False

def convert_boolean_value(value):
    """Normalize booleans for PostgreSQL."""
    if value == 1 or value is True:
        return True
    if value == 0 or value is False:
        return False
    return value

def convert_boolean_condition(condition):
    """Convert numeric boolean literals to PostgreSQL booleans."""
    condition = re.sub(r" = 1(?![0-9])", " = true", condition)
    condition = re.sub(r" = 0(?![0-9.])", " = false", condition)
    condition = re.sub(r"= 1(?![0-9])", "= true", condition)
    condition = re.sub(r"= 0(?![0-9.])", "= false", condition)
    return condition

def cursorInstance():
  if not IS_POSTGRESQL or not DATABASE_URL:
    raise RuntimeError(
      "DATABASE_URL must be set to a PostgreSQL DSN. SQLite fallback has been removed."
    )
  import psycopg2

  # Pass the full DSN so query params (e.g. sslmode=require from Render) are preserved.
  conn = psycopg2.connect(DATABASE_URL, connect_timeout=30)
  return conn, conn.cursor()

