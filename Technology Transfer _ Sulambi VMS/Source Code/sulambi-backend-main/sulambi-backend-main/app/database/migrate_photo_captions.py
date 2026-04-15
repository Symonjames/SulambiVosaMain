"""
Migration script to add photoCaptions column to existing report tables
Run this script to update existing databases with the new photoCaptions column
"""

from . import connection
from dotenv import load_dotenv
import os

load_dotenv()
DEBUG = os.getenv("DEBUG") == "True"
conn, cursor = connection.cursorInstance()

def migrate_photo_captions():
    """Add photoCaptions column to report tables if it doesn't exist (PostgreSQL only)."""

    from .connection import DATABASE_URL
    from .connection import is_postgresql_url
    is_postgresql = is_postgresql_url(DATABASE_URL)
    if not is_postgresql:
        raise RuntimeError("PostgreSQL DATABASE_URL is required. SQLite mode is not supported.")

    try:
        # Check if photoCaptions column exists in externalReport table
        # PostgreSQL: use information_schema
        from .connection import quote_identifier
        external_table = quote_identifier('externalReport')
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s 
            AND lower(column_name) = 'photocaptions'
        """, (external_table.strip('"'),))
        external_columns = [row[0] for row in cursor.fetchall()]
        
        if 'photoCaptions' not in external_columns:
            DEBUG and print("[*] Adding photoCaptions column to externalReport table...", end="")
            from .connection import quote_identifier
            external_table = quote_identifier('externalReport')
            cursor.execute(f'ALTER TABLE {external_table} ADD COLUMN photoCaptions TEXT')
            DEBUG and print("Done")
        else:
            DEBUG and print("[*] photoCaptions column already exists in externalReport table")
        
        # Check if photoCaptions column exists in internalReport table
        # PostgreSQL: use information_schema
        from .connection import quote_identifier
        internal_table = quote_identifier('internalReport')
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s 
            AND lower(column_name) = 'photocaptions'
        """, (internal_table.strip('"'),))
        internal_columns = [row[0] for row in cursor.fetchall()]
        
        if 'photoCaptions' not in internal_columns:
            DEBUG and print("[*] Adding photoCaptions column to internalReport table...", end="")
            from .connection import quote_identifier
            internal_table = quote_identifier('internalReport')
            cursor.execute(f'ALTER TABLE {internal_table} ADD COLUMN photoCaptions TEXT')
            DEBUG and print("Done")
        else:
            DEBUG and print("[*] photoCaptions column already exists in internalReport table")
        
        # Commit changes
        conn.commit()
        DEBUG and print("[*] Migration completed successfully!")
        
    except Exception as e:
        DEBUG and print(f"[!] Migration failed: {str(e)}")
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_photo_captions()
