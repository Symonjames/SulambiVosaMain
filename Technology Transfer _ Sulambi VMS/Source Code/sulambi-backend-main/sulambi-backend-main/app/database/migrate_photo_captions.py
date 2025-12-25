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
    """Add photoCaptions column to existing report tables if it doesn't exist"""
    
    try:
        # Check if photoCaptions column exists in externalReport table
        cursor.execute("PRAGMA table_info(externalReport)")
        external_columns = [column[1] for column in cursor.fetchall()]
        
        if 'photoCaptions' not in external_columns:
            DEBUG and print("[*] Adding photoCaptions column to externalReport table...", end="")
            conn.execute("ALTER TABLE externalReport ADD COLUMN photoCaptions TEXT")
            DEBUG and print("Done")
        else:
            DEBUG and print("[*] photoCaptions column already exists in externalReport table")
        
        # Check if photoCaptions column exists in internalReport table
        cursor.execute("PRAGMA table_info(internalReport)")
        internal_columns = [column[1] for column in cursor.fetchall()]
        
        if 'photoCaptions' not in internal_columns:
            DEBUG and print("[*] Adding photoCaptions column to internalReport table...", end="")
            conn.execute("ALTER TABLE internalReport ADD COLUMN photoCaptions TEXT")
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
