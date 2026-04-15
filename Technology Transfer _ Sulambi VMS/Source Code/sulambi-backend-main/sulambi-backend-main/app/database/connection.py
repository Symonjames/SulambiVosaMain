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
_TABLE_NAME_CACHE: dict[str, str] = {}

def quote_identifier(identifier):
    """Normalize identifiers for PostgreSQL (unquoted lowercase)."""
    return identifier.lower()

def table_name_for_query(identifier):
    """
    Resolve a PostgreSQL table name safely.
    - If exact mixed-case table exists, return quoted exact name.
    - Else if lowercase exists, return lowercase.
    - Else fallback to lowercase (legacy behavior).
    """
    key = str(identifier or "")
    if not key:
        return key
    if key in _TABLE_NAME_CACHE:
        return _TABLE_NAME_CACHE[key]

    lower = key.lower()
    try:
        conn, cursor = cursorInstance()
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND (table_name = %s OR table_name = %s)
            LIMIT 2
            """,
            (key, lower),
        )
        names = {row[0] for row in cursor.fetchall()}
        conn.close()
        if key in names:
            resolved = f'"{key}"'
        elif lower in names:
            resolved = lower
        else:
            resolved = lower
    except Exception:
        resolved = lower

    _TABLE_NAME_CACHE[key] = resolved
    return resolved

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
  from urllib.parse import urlparse

  result = urlparse(DATABASE_URL)
  connect = psycopg2.connect(
    database=result.path[1:],  # Remove leading '/'
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port or 5432,
    connect_timeout=15
  )
  return connect, connect.cursor()

