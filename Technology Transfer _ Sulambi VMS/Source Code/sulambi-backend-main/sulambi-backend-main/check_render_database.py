#!/usr/bin/env python3
"""
Quick check to see if data exists in Render PostgreSQL database
Run this locally with DATABASE_URL set to your Render External Database URL
"""

import os
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    print("\nTo get your DATABASE_URL:")
    print("1. Go to Render Dashboard → sulambi-database")
    print("2. Click on 'Connection Info' tab")
    print("3. Copy the 'External Database URL' (for connecting from local machine)")
    print("\nThen set it as:")
    print("  Windows PowerShell: $env:DATABASE_URL = 'your-connection-string'")
    print("  Or create a .env file with: DATABASE_URL=your-connection-string")
    sys.exit(1)

try:
    import psycopg2
    result = urlparse(DATABASE_URL)
    
    print("=" * 70)
    print("CHECKING RENDER POSTGRESQL DATABASE")
    print("=" * 70)
    print(f"Host: {result.hostname}")
    print(f"Database: {result.path[1:]}")
    print("=" * 70)
    
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port or 5432
    )
    cursor = conn.cursor()
    print("✓ Connected successfully!\n")
    
    # Get all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} tables:\n")
    
    # Check each table for data
    total_rows = 0
    for (table_name,) in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_rows += count
            status = "✅" if count > 0 else "⚪"
            print(f"  {status} {table_name}: {count} rows")
        except Exception as e:
            print(f"  ❌ {table_name}: Error - {e}")
    
    print("\n" + "=" * 70)
    print(f"TOTAL ROWS: {total_rows}")
    print("=" * 70)
    
    if total_rows == 0:
        print("\n⚠️  DATABASE IS EMPTY - Migration not completed yet!")
        print("\nTo migrate your SQLite data:")
        print("1. Make sure your backend has created the tables (should be automatic)")
        print("2. Run: python migrate_sqlite_to_postgresql.py")
        print("3. Use the External Database URL from Render")
    else:
        print("\n✅ Database has data! Migration appears to be complete.")
        print("\nKey tables to check:")
        key_tables = ['accounts', 'membership', 'internalEvents', 'externalEvents']
        for table in key_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  - {table}: {count} rows")
            except:
                pass
    
    cursor.close()
    conn.close()
    
except ImportError:
    print("❌ ERROR: psycopg2 not installed. Install with: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR connecting to database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

